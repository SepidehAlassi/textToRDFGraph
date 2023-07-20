import unittest
from pipes.preprocess_pipe import detect_lang


class InputLanguageTest(unittest.TestCase):
    def test_supported_lang(self):
        lang = detect_lang("hallo meine Liebe, wie geht es dir?")
        self.assertEqual(lang, 'de')

    def test_unsupported_lang(self):
        text = "De voila baguette dans frenchtech manger un camembert putain. Comme même être carrément quand même vouloir putain du coup. Du vin."
        self.assertRaises(ValueError, detect_lang, text)


if __name__ == '__main__':
    unittest.main()
