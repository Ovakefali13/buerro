import unittest
from unittest import defaultTestLoader
import coverage
import os
from argparse import ArgumentParser

def main(arg_module=None):
    if arg_module:
        modules = [arg_module]
    else:
        modules = ['services', 'usecase', 'chatbot', 'controller', 'handler']

    cov = coverage.Coverage(source=modules, branch=True)
    cov.start()

    dir_path = os.path.dirname(os.path.realpath(__file__))

    suites = [defaultTestLoader.discover(m, top_level_dir=dir_path) for m in modules]
    suite = unittest.TestSuite(suites)
    runner = unittest.TextTestRunner(verbosity=2)
    results = runner.run(suite)

    cov.stop()
    cov.save()
    print(cov.report())

    if results.errors or results.failures:
        exit(1)
    else:
        exit(0)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-m","--module", dest="arg_module", default=None,
                            help="build a single module")
    args = parser.parse_args()
    main(args.arg_module)
