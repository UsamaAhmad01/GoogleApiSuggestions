import unittest
from GoogleSuggestonApi import criteria_for_miss_spells 

class TestCriteriaForMissSpells(unittest.TestCase):

    def test_keyword_in_suggestions(self):
        keyword = 'usama'
        suggestions = ["usama mir","usama khan","usama name meaning in urdu","usama"]
        
        result = criteria_for_miss_spells(keyword, suggestions)
        
        expected_result = {
            "keyword": keyword,
            "suggestions": suggestions,
            "is_misspelled": False,
            "correct_keyword": None,
        }
        
        self.assertEqual(result, expected_result)

    def test_short_keyword(self):
        keyword = 'ab'
        suggestions = ["abbottabad weather","abl","abbottabad","abc","abdullah kadwani","a"]
        
        result = criteria_for_miss_spells(keyword, suggestions)
        
        expected_result = {
            'keyword': keyword,
            'suggestions': suggestions,
            'is_misspelled': False,
            'correct_keyword': None
        }
        
        self.assertEqual(result, expected_result)

    def test_order_present(self):
        keyword = '15 phone'
        suggestions = ["15 phone pro","15 phone","15 phone plan","15 phone country code"]
        
        result = criteria_for_miss_spells(keyword, suggestions)
        
        expected_result = {
            'keyword': keyword,
            'suggestions': suggestions,
            'is_misspelled': False,
            'correct_keyword': None
        }
        
        self.assertEqual(result, expected_result)

    def test_order_not_present(self):
        keyword = 'iphone 15 '
        suggestions = ["iphone 13","abcfabrics. com. pk","abc fitness.com.pk","abc fabrics.com.pk","abc fullname.com"]
        
        result = criteria_for_miss_spells(keyword, suggestions)
        
        expected_result = {
            'keyword': keyword,
            'suggestions': suggestions,
            'is_misspelled': True,
            'correct_keyword': "iphone 13",
        }
        
        self.assertEqual(result, expected_result)

    def test_empty_suggestions(self):
        keyword = 'pythrone'
        suggestions = []
        
        result = criteria_for_miss_spells(keyword, suggestions)
        
        expected_result = {
            'keyword': keyword,
            'data_found': False,
            'is_misspelled': "",
            'correct_keyword': "",
        }
        
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()


