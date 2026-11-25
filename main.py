#!/usr/bin/env python3
"""One Line, Big Laugh — write the hilarious line to entry.txt.

Run plain to write entry.txt into $MAKEFUN_OUTPUT_DIR (or the current
directory if that is unset). `--check` only validates the line;
`--self-test` runs the built-in checks, including the bad inputs that
must be refused.

Gate: the line is the whole entry, one line, at most 200 characters.
Every write is followed by reading the file back and re-checking it,
so what the judge sees is exactly the line below.
"""

import os
import sys
import tempfile

JOKE = (
    "I asked AI to write my wedding vows; "
    "it said my love was beautiful but suggested "
    "I upgrade to premium first."
)

MAX_LENGTH = 200

# Each rule is (label, test): the test answers True for a legal line.
RULES = [
    ("non-empty", lambda s: s.strip() != ""),
    ("no edge whitespace", lambda s: s == s.strip()),
    ("single line", lambda s: "\n" not in s and "\r" not in s),
    ("at most 200 characters", lambda s: 1 <= len(s) <= MAX_LENGTH),
    ("ends with a full stop", lambda s: s.endswith(".")),
]


def broken(line):
    """Names of the rules `line` breaks; empty means the line is legal."""
    return [label for label, test in RULES if not test(line)]


def check():
    bad = broken(JOKE)
    if bad:
        for label in bad:
            print("check failed: %s" % label, file=sys.stderr)
        return 1
    print("check ok: %d characters" % len(JOKE))
    return 0


def write(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8") as stream:
        stream.write(JOKE + "\n")
    with open(path, encoding="utf-8") as stream:
        saved = stream.read()
    if saved != JOKE + "\n":
        print("error: entry.txt does not match the line", file=sys.stderr)
        return 1
    bad = broken(saved.rstrip("\n"))
    if bad:
        for label in bad:
            print("check failed: %s" % label, file=sys.stderr)
        return 1
    if len(saved) > MAX_LENGTH + 1:
        print("error: entry.txt is over the character gate", file=sys.stderr)
        return 1
    print("wrote %s" % path)
    return 0


def self_test():
    if check() != 0:
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        if write(tmp) != 0:
            return 1
        with open(os.path.join(tmp, "entry.txt"), encoding="utf-8") as stream:
            if stream.read() != JOKE + "\n":
                print("self-test failed: round-trip mismatch", file=sys.stderr)
                return 1
    rejects = ["", "  x  ", "y" * (MAX_LENGTH + 1), "a\nb", "\tTabbed"]
    for candidate in rejects:
        if not broken(candidate):
            print(
                "self-test failed: accepted %r" % candidate[:20],
                file=sys.stderr,
            )
            return 1
    print("self-test ok")
    return 0


def usage():
    print(__doc__.split("\n\n")[1])
    print("  python3 main.py [--check | --self-test]")


def main(argv):
    if "--help" in argv or "-h" in argv:
        usage()
        return 0
    if "--self-test" in argv:
        return self_test()
    if "--check" in argv:
        return check()
    if argv:
        print("error: unknown option %s" % argv[0], file=sys.stderr)
        return 2
    return write(os.environ.get("MAKEFUN_OUTPUT_DIR", "."))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
