#!/usr/bin/env python3
import os
import sys
import unittest

import xmlrunner


def main() -> None:
    """
    Run unittests and generate JUnit XML
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    tests_dir = os.path.join(project_root, "tests")
    sys.path.insert(0, tests_dir)

    loader = unittest.TestLoader()
    suite = loader.discover(
        start_dir=tests_dir,
        pattern="test_*.py",
        top_level_dir=project_root,
    )

    runner = xmlrunner.XMLTestRunner(
        output=os.path.join(project_root, "junit"),
        verbosity=2,
    )

    result = runner.run(suite)
    sys.exit(not result.wasSuccessful())


if __name__ == "__main__":
    main()
