import nltk
import copy
import collections

def update_text(in_text, in_constant_phrases):
    result_text = []
    for sentence in in_text:
        new_sentence = []
        words_deque = collections.deque(sentence)
        
        while len(words_deque):
            if len(words_deque) > 1 and (words_deque[0], words_deque[1]) in in_constant_phrases:
                new_sentence.append(' '.join([words_deque[0], words_deque[1]]))
                words_deque.popleft()
                words_deque.popleft()
            else:
                new_sentence.append(words_deque[0])
                words_deque.popleft()
        result_text.append(new_sentence)
    return result_text

# merging only constant bigrams while they do exist in the text
def merge_contact_phrases(in_text):
    text = in_text
    
    constant_phrases_exist = True
    while constant_phrases_exist:
        bigram_freqs = collections.defaultdict(lambda: 0)
        unigram_freqs = collections.defaultdict(lambda: 0)
        for sentence in text:
            for word in sentence:
                unigram_freqs[word] += 1
            for bigram in nltk.bigrams(sentence):
                bigram_freqs[bigram] += 1
        constant_phrases = set([])
        for bigram in bigram_freqs:
            if bigram_freqs[bigram] == unigram_freqs[bigram[0]] and \
               bigram_freqs[bigram] == unigram_freqs[bigram[1]]:
                constant_phrases.add(bigram)
        if len(constant_phrases):
            text = update_text(text, constant_phrases)
        else:
            constant_phrases_exist = False
    return text

def add_merged_lexemes_pair(in_const_phrases, in_lex_a, in_lex_b):
    for const_phrase in in_const_phrases:
        # adding both lexemes to the phrase keeping it sorted and duplicate-free
        if in_lex_a in const_phrase or in_lex_b in const_phrase:
            const_phrase[:] = sorted(set(const_phrase.extend([in_lex_a, in_lex_b])))
            return
    in_const_phrases.append(sorted([in_lex_a, in_lex_b]))

# merges constant phrases by lexemes' existence areas
def extract_constant_phrases(in_existence_areas):
    # stores lists [id1, id2, ...] of merged lexemes
    const_phrases = []
    lexeme_ids = sorted(in_existence_areas.keys())
    for index_i in xrange(len(lexeme_ids)):
        for index_j in xrange(index_i + 1, len(lexeme_ids)):
            (lex_a, lex_b) = (lexeme_ids[index_i], lexeme_ids[index_j])
            if in_existence_areas[lex_a] == in_existence_areas[lex_b]:
                add_merged_lexemes_pair(const_phrases, 
                                        lexeme_ids[index_i],
                                        lexeme_ids[index_j])
    return const_phrases

def test_contact_phrases():
    text = [['cat', 'walks', 'the', 'street', 'every', 'day'],
            ['and', 'another', 'cat', 'walks', 'the', 'town', 'every', 'day']]
    
    assert(merge_constant_phrases(text) == [['cat walks the', 'street', 'every day'], 
        ['and another', 'cat walks the', 'town', 'every day']])
    print 'test OK'

def test():
    text = [[1, 2, 4, 5], [2, 3, 1], [1, 5, 6, 2]]
    existence_areas = {1: [0, 1, 2], 2: [0, 1, 2], 3: [1], 4: [0], 5: [0, 2], 6: [2]}
    assert(extract_constant_phrases(existence_areas) == [[1, 2]])
    print 'Test OK'

if __name__ == '__main__':
    test()
