import unittest
import os
from stage2 import entities_fromJson

json_file = os.path.join(os.getcwd(), 'test.json')


class MyTestCase(unittest.TestCase):
    def test_read_entities(self):
        output = entities_fromJson(json_file)
        pers = output['Persons']['118509950'][0]
        self.assertEqual(pers.givenName, 'Jakob')  # add assertion here


if __name__ == '__main__':
    unittest.main()
