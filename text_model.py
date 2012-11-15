import re
import collections
import copy
import nltk.tokenize

import common
import link_lexemes
import const_phrase

# calculating critical frequency for arbitrarily built frequency dictionary
# (may be raw frequency as well as assotiative power)
def calculate_critical_frequency(in_freq_dictionary):
    distinct_frequencies = set(in_freq_dictionary.values())
    max_rank = len(distinct_frequencies)
    return 1.0 + 0.5 * max_rank

# returns a list of sentences, each one being a list of words, free of punctuation marks
def tokenize_sentences(in_raw_text):
    # splitting sentences
    sentences = nltk.tokenize.sent_tokenize(in_raw_text)
    
    # splitting words, removing punctuation
    punct_free_sentences = []
    for sentence in sentences:
        tokens = nltk.tokenize.wordpunct_tokenize(sentence)
        punct_free_sentences.append([word.lower() for word in tokens if re.findall('\w+', word)])
    return punct_free_sentences

def write_text(in_stream, in_sentences):
    for sentence in in_sentences:
        print >>in_stream, ' '.join(sentence)

# every tuple of lexemes with equal existence matrices is a constant phrase
def extract_constant_phrases(in_existence_areas):
    ids_sorted = sorted(in_existence_areas.keys())
    id_indices_used = set([])
    constant_phrases = []
    for head_index in xrange(len(ids_sorted)):
        if head_index in id_indices_used:
            continue
        head = ids_sorted[head_index]
        constant_phrase_context = []
        for context_index in xrange(head_index + 1, len(ids_sorted)):
            context = ids_sorted[context_index]
            if in_existence_areas[head] == in_existence_areas[context] \
                and context_index not in id_indices_used:
                constant_phrase_context.append(context)
                id_indices_used.add(context_index)
        if len(constant_phrase_context):
            constant_phrases.append([head] + constant_phrase_context)
            id_indices_used.add(head_index)
    return constant_phrases

def refresh_text_index(in_lexemes, in_text_index):
        new_text = {}
        # removing links to non-existent lexemes
        for id in in_text_index:
            new_text[id] = \
                [word_id for word_id in in_text_index[id] if word_id in in_lexemes]
        # removing empty sentences
        text_dict = {id: words for (id, words) in new_text.iteritems() if len(words)}
        return text_dict

def lexeme_associative_power(in_lexeme_id, in_text_index):
    # here area does not include the generative sentence (which the first appearance is in)
    adjacent_lexemes = set([])
    for sentence_id in in_text_index:
        if in_lexeme_id in in_text_index[sentence_id]:
            adjacent_lexemes.update(set(in_text_index[sentence_id]))
    # removing from the result the id of the target itself
    adjacent_lexemes.remove(in_lexeme_id)
    return len(adjacent_lexemes)

# dumps two lists of dominant and nondominant lexemes with their associative powers
def dump_lexemes(in_text_model):
    dominant_lexemes = {}
    nondominant_lexemes = {}
    for position in in_text_model.existence_areas.keys():
        lexeme = in_text_model.pos_to_lex_mapping[position]
        power = in_text_model.associative_power_dict[position]
        if power > in_text_model.critical_associative_power:
            dominant_lexemes[lexeme] = power
        else:
            nondominant_lexemes[lexeme] = power
    return (sorted(dominant_lexemes.items(), key = operator.itemgetter(1), reverse = True),
            sorted(nondominant_lexemes.items(), key = operator.itemgetter(1), reverse = True))

class AssociativeModel(object):
    def __init__(self, in_sentences, in_language = common.DEFAULT_LANGUAGE):
        self.language = in_language
        self.sentences = copy.deepcopy(in_sentences)
        '''
            builds:
            self.fls - full link set in the form ['word', start_position]
            self.pos_to_lex_mapping for words from fls: {start_position -> 'word'}
            self.lex_to_pos_mapping for words from fls: {'word' -> start_position}
            self.indexed_text: sentences containing positions of fls' lexemes held inside of them
        '''
        self.initial_preprocessing(self.sentences)

        self.existence_areas = self.calculate_existence_areas(self.indexed_text,
                                                              self.pos_to_lex_mapping)
        self.associative_power_dict = self.calculate_associative_power(self.indexed_text,
                                                                       self.existence_areas)
        self.critical_associative_power = calculate_critical_frequency(self.associative_power_dict)
        # removing attributive lexemes, merging constant phrases
        self.existence_areas = self.perform_existence_areas_analysis(self.existence_areas)

    # extracting full link set
    def initial_preprocessing(self, in_sentences):
        # just words in the right order
        self.fls = link_lexemes.extract_full_link_set(in_sentences,
                                                      self.language,
                                                      keep_positions = True)
        self.pos_to_lex_mapping = {record[1]:record[0] for record in self.fls}
        self.lex_to_pos_mapping = {record[0]:record[1] for record in self.fls}

        # representing sentences as lists of FLS indices, not words themselves
        self.indexed_text = self.build_text_index(in_sentences, self.lex_to_pos_mapping)

    def build_text_index(self, in_sentences, in_mapping):
        indexed_sentences = []
        for sentence in in_sentences:
            new_sentence = ([in_mapping[word] for word in sentence if word in in_mapping])
            if len(new_sentence):
                indexed_sentences.append(new_sentence)
        return indexed_sentences

    def merge_constant_phrases(self, in_existence_areas):
        const_phrases = const_phrase.extract_constant_phrases(in_existence_areas)

    def is_attributive_lexeme(self, in_id):
        target_area = set(self.existence_areas[in_id])
        for lexeme_id in self.existence_areas.keys():
            if not lexeme_id == in_id:
                other_area = set(self.existence_areas[lexeme_id])
                if not len(target_area.difference(other_area)) \
                    and len(other_area.difference(target_area)):
                    return True
        return False

    # filtering off attributive lexemes, merging constant phrases
    def perform_existence_areas_analysis(self, in_existence_areas):
        nonattributive = self.extract_nonattributive_lexemes(in_existence_areas)
        merged = self.merge_const_phrases(nonattributive)
        return merged

    def merge_const_phrases(self, in_existence_areas):
        # detecting constant phrases
        phrases_merged = const_phrase.extract_constant_phrases(in_existence_areas)
        lexemes_to_remove = set([])
        for phrase in phrases_merged:
            lexemes_to_remove |= set(phrase[1:])
        return {lex_id: area for (lex_id, area) in in_existence_areas.iteritems() \
                if lex_id not in lexemes_to_remove}

    def extract_nonattributive_lexemes(self, in_existence_areas):
        return {lexeme_id: area for (lexeme_id, area) in in_existence_areas.iteritems() \
                if not self.is_attributive_lexeme(lexeme_id)}

    '''
        returns a mapping: 'lexeme ID' -> [sentence ids]
    '''
    def calculate_existence_areas(self, in_indexed_text, in_pos_to_lex_mapping):
        existence_areas = collections.defaultdict(lambda: set([]))
        for index in xrange(len(in_indexed_text)):
            for word_id in in_indexed_text[index]:
                if word_id in in_pos_to_lex_mapping:
                    existence_areas[word_id].add(index)
        # sorting sets
        result_areas = {word_id: sorted(sent_ids) \
            for (word_id, sent_ids) in sorted(existence_areas.iteritems())}
        return result_areas

    def refresh_text_index(self):
        self.indexed_text = refresh_text_index(self.active_lexemes, self.indexed_text)

    '''
        Returns a map:
        {lexeme_id -> # unique adjacent lexemes within all the sentences except for the generative one}
    '''
    def calculate_associative_power(self, in_indexed_text, in_existence_areas):
        result = {}
        for lexeme_id in in_existence_areas:
            # we do not count generative sentence while computing associative power
            existence_area = in_existence_areas[lexeme_id][1:]
            result[lexeme_id] = len(existence_area) - 1
        return result

    def remove_nondominants(self):
        dominant_ids = set(extract_dominants(self.indexed_text, self.active_lexemes))
        nondominant_ids = set(self.active_lexemes.keys()).difference(dominant_ids)
        for id in nondominant_ids:
            self.active_lexemes.pop(id)
        
        for id in self.sentences:
            self.sentences[id][:] = [word_id for word_id in self.sentences[id] \
                if word_id in self.active_lexemes]

        self.refresh_text_index()
        self.calculate_existence_areas()

    def text_as_string(self):
        result_text = []
        for sentence_id in sorted(self.sentences.keys()):
            for word_id in self.sentences[sentence_id]:
                result_text.append(self.active_lexemes[word_id])
            result_text.append('.')
        return '\t'.join(result_text)

def test():
    lexemes = [['mom', 'dad', 'dog', 'cat']]
    filtering_set = ['dad', 'cat']
    print stop(lexemes, in_filtering_set = filtering_set)

if __name__ == '__main__':
    test()
