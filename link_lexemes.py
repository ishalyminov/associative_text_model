import collections
import operator
import itertools
import nltk.corpus

'''
    Full link set of lexemes is the lexemes which:
    1) are not stopwords,
    2) have the frequency of > 1 (multiple appearances within the same sentence are not counted).
'''

NO_POSITION = -1

def tuples_list_uniq(in_tuples_list, in_target_field = 0):
    result = []
    seen_lexemas = set([])
    for value in in_tuples_list:
        if value[in_target_field] not in seen_lexemas:
            result.append(value)
            seen_lexemas.add(value[in_target_field])
    return result

def stop(in_sentences, in_language):
    result = []
    stopwords = nltk.corpus.stopwords.words(in_language)
    for sentence in in_sentences:
        result.append([word_tuple for word_tuple in sentence if word_tuple[0] not in stopwords])
    return result

def extract_full_link_set(in_sentences,
                          in_language,
                          keep_positions = False,
                          keep_counts = False,
                          stopping = True):
    # lexemes of full link set must be sorted by appearance in the text
    lexeme_positions = {}
    lexeme_counts = collections.defaultdict(lambda: 0)

    position = itertools.count()
    positioned_sentences = []
    for sentence in in_sentences:
        # generating the 'position-word' tuples out of a single sentence's words
        positioned_sentences.append([(word, pos) for word, pos in zip(sentence, position)])

    final_sentences = [tuples_list_uniq(sentence) for sentence in positioned_sentences[:]]
    if stopping:
        final_sentences = stop(final_sentences, in_language)

    for sentence in final_sentences:
        for word in sentence:
            # remembering the first appearance for each lexeme
            if word[0] not in lexeme_positions:
                lexeme_positions[word[0]] = word[1]
            lexeme_counts[word[0]] += 1

    # making a list of tuples (word, position) sorted by position
    sorted_positions = sorted(lexeme_positions.iteritems(), key = operator.itemgetter(1))

    result = [[word] for (word, position) in sorted_positions if lexeme_counts[word] > 1]
    if keep_positions:
        for lexeme_tuple in result:
            lexeme_tuple.append(lexeme_positions[lexeme_tuple[0]])
    if keep_counts:
        for lexeme_tuple in result:
            lexeme_tuple.append(lexeme_counts[lexeme_tuple[0]])
    return result

def test():
    text = [['a', 'man', 'going', 'down', 'a', 'street'], 
            ['a', 'street', 'falling', 'down', 'the', 'cat']]
    assert(extract_full_link_set(text, 'english', stopping=False) == ['a', 'down', 'street'])
    print 'Test OK'
    
if __name__ =='__main__':
    test()
