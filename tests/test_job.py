import unittest

from job import *

OUTPUT = """LROB to LRSV
Job ID 12345
Type of cargo kg
Cargo Amount 1 kg/s
Payment $100
Expires 20/05/2019"""


class job_import_test(unittest.TestCase):
    def test___str__(self):
        test_job = Job(12345, 'LR0B', 'LRSV', 'LROB', '1', 'kg', 'boxes of fish', '100', '20/05/2019', 'no', 'Trip-Only', '54321')
        print(test_job)
        self.assertMultiLineEqual(test_job.__str__(), OUTPUT)


if __name__ == '__main__':
    unittest.main()
