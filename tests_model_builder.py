import unittest
from model_builder import *
import link_lexemes
import operator

class FullLinkSetExtractionTest(unittest.TestCase):
    INPUT_FILE = 'tests/input.txt'
    ANSWER_FILE = 'tests/fls_extraction_answer.txt'
    def setUp(self):
        raw_text = ' '.join([line.strip() for line in open(FullLinkSetExtractionTest.INPUT_FILE)])
        self.sentences = stop(tokenize_sentences(raw_text))
        self.answer = [(line.strip().split()[0], int(line.strip().split()[1])) \
            for line in open(FullLinkSetExtractionTest.ANSWER_FILE)]
        
    def test_extraction(self):
        self.assertEqual(link_lexemes.extract_full_link_set(self.sentences, True), self.answer)

class ExistenceAreasCalculationTest(unittest.TestCase):
    INPUT_FILE = 'tests/input.txt'
    ANSWER_FILE = 'tests/existence_areas_calc_answer.txt'
    
    def get_existence_areas(self, in_indexed_text, in_lexemes):
        areas_dict = calculate_existence_areas(in_indexed_text, in_lexemes)
        result = [value for (key, value) in sorted(areas_dict.iteritems(), key = operator.itemgetter(0))]
        return result

    def setUp(self):
        raw_text = ' '.join([line.strip() for line in open(ExistenceAreasCalculationTest.INPUT_FILE)])
        self.sentences = stop(tokenize_sentences(raw_text))
        self.answer = [[int(index) for index in line.strip().split()[1:]] \
            for line in open(ExistenceAreasCalculationTest.ANSWER_FILE)]

    def test_extraction(self):
        fls = make_lexemes_dict(link_lexemes.extract_full_link_set(self.sentences))
        indexed_text = build_text_index(self.sentences, fls)
        self.assertEqual(self.get_existence_areas(indexed_text, fls), self.answer)

class ConstantPhraseTest(unittest.TestCase):
    INPUT_FILE = 'tests/input.txt'
    
    def setUp(self):
        raw_text = ' '.join([line.strip() for line in open(ExistenceAreasCalculationTest.INPUT_FILE)])
        self.sentences = stop(tokenize_sentences(raw_text))
        self.fls = make_lexemes_dict(link_lexemes.extract_full_link_set(self.sentences))
        self.indexed_text = build_text_index(self.sentences, self.fls)
        existence_areas = calculate_existence_areas(self.indexed_text, self.fls)
        self.const_phrases = extract_constant_phrases(existence_areas)

    def test_extraction(self):
        answer = [[int(index) for index in line.strip().split()] \
            for line in open('tests/const_phrase_answer.txt')]
        self.assertEqual(self.const_phrases, answer)
    
    def test_merge(self):
        answer = [[int(index) for index in line.strip().split()] \
            for line in open('tests/const_phrase_merge_answer.txt')]
        (lexemes_merged, text_merged) = \
            merge_constant_phrases(self.fls, self.indexed_text, self.const_phrases)
        self.assertEqual([words for (id, words) in sorted(text_merged.iteritems())], answer)

class AssociativePowerTest(unittest.TestCase):
    INPUT_FILE = 'tests/input.txt'
    
    def setUp(self):
        raw_text = ' '.join([line.strip() for line in open(ExistenceAreasCalculationTest.INPUT_FILE)])
        self.sentences = stop(tokenize_sentences(raw_text))
        self.fls = make_lexemes_dict(link_lexemes.extract_full_link_set(self.sentences))
        self.indexed_text = build_text_index(self.sentences, self.fls)
        self.lexeme_powers = {id: lexeme_associative_power(id, self.indexed_text) \
            for id in self.fls}
    
    def test_lexeme_powers(self):
        answer = [int(line.strip()) for line in open('tests/associative_power_answer.txt')]
        self.assertEqual(answer, self.lexeme_powers.values())
    
    def test_dominant_lexemes(self):
        self.assertEqual(extract_dominants(self.indexed_text, self.fls), self.fls.keys())


if __name__ == '__main__':
    unittest.main()