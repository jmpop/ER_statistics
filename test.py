# from ER_apis.test import *
# from ER_datas.test import *
import unittest

print("b")
class TestForeignTeam(unittest.TestCase):
    def test_true(self):
        print("e")
        self.assertEqual(1, 1)

if __name__ == "__main__":
    unittest.main()
