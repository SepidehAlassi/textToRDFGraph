import unittest
from Entitiy import PersonEntity, GeoEntity

class MyTestCase(unittest.TestCase):
    def test_something(self):
        entity = PersonEntity("something", "jshgkjg")
        entity.population = 20000
        setattr(entity, 'text', 'a new text')
        attribs = vars(entity)
        self.assertEqual(entity.population, 20000)


if __name__ == '__main__':
    unittest.main()
