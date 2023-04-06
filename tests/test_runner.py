import unittest

from tests import ServerUtilsTest

testLoad = unittest.TestLoader()
suites = testLoad.loadTestsFromTestCase(ServerUtilsTest)

runner = unittest.TextTestRunner(verbosity=2)

if __name__ == '__main__':
    runner.run(suites)