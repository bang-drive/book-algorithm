import os
import shutil
import sys
import unittest


class Flake8Test(unittest.TestCase):

    def test_flake8(self):
        binary = 'flake8'
        self.assertIsNotNone(shutil.which(binary), F'Cannot find {binary}. Please install it.')

        failed_targets = [target for target in sys.argv[1:] if 0 != os.system(F'{binary} {target}')]
        self.assertEqual(
            len(failed_targets), 0,
            F'Lint failed for following targets, please run "{binary}" to check and fix:\n' +
            '\n'.join(failed_targets))


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
