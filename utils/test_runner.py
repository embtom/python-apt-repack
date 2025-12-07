#!/usr/bin/env python3
import os
import unittest


def main() -> None:
    """
    Run unittests
    """
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    unittest.main(
        module=None,
        argv=[
            "python-apt-test",
            "discover",
            "-s",
            "tests",
            "-p",
            "test_*.py",
        ],
    )


if __name__ == "__main__":
    main()
