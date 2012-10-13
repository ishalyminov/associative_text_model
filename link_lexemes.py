import collections
import operator

'''
    Full link set of lexemes is actually a list of lexemes which appear in text more than once.
    Multiple appearances within a sentence are not counted.
'''

NO_POSITION = -1

# input tuples are of the form (position, word)
def tuples_list_uniq(in_tuples_list):
    result = []
    seen_lexemas = set([])
    for tuple in in_tuples_list:
        if tuple[1] not in seen_lexemas:
            result.append(tuple)
            seen_lexemas.add(tuple[1])
    return result

def extract_full_link_set(in_sentences, in_keep_counts=False):
    class Counter(object):
        def __init__(self, in_initial = 0):
            self.value = in_initial
        
        def get_value(self):
            old_value = self.value
            self.value += 1
            return old_value
    
    # lexemes of full link set must be sorted by appearance in the text
    lexeme_positions = collections.defaultdict(lambda: NO_POSITION)
    lexeme_counts = collections.defaultdict(lambda: 0)
    
    position = Counter()
    for sentence in in_sentences:
        # generating the 'position-word' tuples out of a single sentence's words
        positioned_lexemes = [(position.get_value(), word) for word in sentence]
        # uniquifying them by word
        positioned_lexemes_uniq = tuples_list_uniq(positioned_lexemes)
        
        for word in positioned_lexemes_uniq:
            # remembering the first appearance for each lexeme
            if lexeme_positions[word[1]] == -1:
                lexeme_positions[word[1]] = word[0]
            lexeme_counts[word[1]] += 1
    
    # making a list of tuples (word, position) sorted by position
    sorted_positions = sorted(lexeme_positions.iteritems(), key=operator.itemgetter(1))
    
    if in_keep_counts:
        result = [(word, lexeme_counts[word]) \
            for (word, position) in sorted_positions if lexeme_counts[word] > 1]
    else:
        result = [word for (word, position) in sorted_positions if lexeme_counts[word] > 1]
    return result

def test():
    text = [['a', 'man', 'going', 'down', 'a', 'street'], 
            ['a', 'street', 'falling', 'down', 'the', 'cat']]
    assert(extract_full_link_set(text) == ['a', 'down', 'street'])
    print 'Test OK'
    
if __name__ =='__main__':
    test()
    