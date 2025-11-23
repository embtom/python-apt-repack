#!/usr/bin/env python3
import unittest


def main():
    """
    Run unittests
    """
    unittest.main(module=None, argv=[
        "python-apt-test",
        "discover",
        "-s", "tests",
        "-p", "test_*.py",
    ])


if __name__ == "__main__":
    main()
