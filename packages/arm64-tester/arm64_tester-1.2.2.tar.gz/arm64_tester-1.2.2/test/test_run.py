import unittest

from arm64_tester import Test


class RunTest(unittest.TestCase):

    def test_run(self):
        submission_path = "./submission.zip"
        subroutine_path = "./subroutine.yaml"
        tests_path = "./tests.yaml"

        test = Test(submission_path, subroutine_path, tests_path)

        print(test.run())
        self.assertTrue(True)
        pass


if __name__ == '__main__':
    unittest.main()
