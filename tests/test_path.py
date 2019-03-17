import unittest

from path import *


class path_import_test(unittest.TestCase):
    def test_shortest_routes(self):
        test_path = Node('LR0B', True, False)
        test_path.add_previous_hop('279599061', 3)
        test_path.add_previous_hop('279599038', 1)
        test_path.add_previous_hop('279599049', 1)
        test_path.add_previous_hop('279599050', 2)
        self.assertEqual(test_path.shortest_routes(), [('279599038', 1), ('279599049', 1)])

    def test_find_lowest_metric(self):
        test_path = Node('LR0B', True, False)
        test_path.add_previous_hop('279599061', 3)
        test_path.add_previous_hop('279599038', 1)
        test_path.add_previous_hop('279599049', 1)
        test_path.add_previous_hop('279599050', 2)
        self.assertEqual(test_path.find_lowest_metric(), 1)


if __name__ == '__main__':
    unittest.main()
