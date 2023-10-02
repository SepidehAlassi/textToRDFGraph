import unittest
from pipes.PreProcessor import detect_lang


class InputLanguageTest(unittest.TestCase):
    def test_de_lang(self):
        lang = detect_lang("hallo meine Liebe, wie geht es dir?")
        self.assertEqual('de', lang)

    def test_en_lang(self):
        text = "The fleet left Spain on 20 September 1519, sailing west across the Atlantic toward South America. " \
               "In December, they made landfall at Rio de Janeiro."
        lang = detect_lang(text)
        self.assertEqual('en', lang)

    def test_fa_lang(self):
        text = "سوئیس از جنوب با ایتالیا، از غرب با فرانسه، از شمال با آلمان و اتریش و از شرق با لیختناشتاین همسایه است. " \
               "بزرگترین شهرها و مراکز اقتصادی سوئیس از جمله  ژنو و بازل در قسمت فلات آن واقع شده اند. برن پایتخت سوئیس است و قطب های اقتصادی آن ژنو و زوریخ هستند."
        lang = detect_lang(text)
        self.assertEqual('fa', lang)

    def test_unsupported_lang(self):
        text = "De voila baguette dans frenchtech manger un camembert putain. Comme même être carrément quand même vouloir putain du coup. Du vin."
        self.assertRaises(ValueError, detect_lang, text)


if __name__ == '__main__':
    unittest.main()
