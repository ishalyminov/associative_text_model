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

# in_text is supposed to be a list of sentences with words tokenized
def merge_constant_phrases(in_text):
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

def test():
    text = [['cat', 'walks', 'the', 'street', 'every', 'day'],
            ['and', 'another', 'cat', 'walks', 'the', 'town', 'every', 'day']]
    
    assert(merge_constant_phrases(text) == [['cat walks the', 'street', 'every day'], 
        ['and another', 'cat walks the', 'town', 'every day']])
    print 'test OK'

if __name__ == '__main__':
    test()
    