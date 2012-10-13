import re
import collections
import copy
import nltk.corpus
import nltk.tokenize
import link_lexemes

STOP_SET = nltk.corpus.stopwords.words('english')

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

def stop(in_text, in_filtering_set=STOP_SET):
    result = []
    for sentence in in_text:
        sentence_filtered = [word for word in sentence if word not in in_filtering_set]
        if len(sentence_filtered):
            result.append(sentence_filtered)
    return result

def write_text(in_stream, in_sentences):
    for sentence in in_sentences:
        print >>in_stream, ' '.join(sentence)

def make_lexemes_dict(in_lexemes_list):
    # a map 'id (i.e. position) -> word'
    result = {}
    for position in xrange(len(in_lexemes_list)):
        result[position] = in_lexemes_list[position]
    return result

'''
    in_indexed_text: dict 'sentence_id' -> 'list of lexeme_ids';
    in_lexemes: dict 'lexeme_id' -> 'string'
'''
def calculate_existence_areas(in_indexed_text, in_lexemes):
    existence_areas = collections.defaultdict(lambda: set([]))
    # just one appearance of a certain word in a single sentence is counted
    for sentence_id in sorted(in_indexed_text.keys()):
        for word_id in in_indexed_text[sentence_id]:
            existence_areas[word_id].add(sentence_id)
    result_areas = {word_id: sorted(sent_ids) \
        for (word_id, sent_ids) in sorted(existence_areas.iteritems())}
    return result_areas

def build_text_index(in_sentences, in_lexemes):
    # inverse mapping for full lexeme set
    word_ids = dict((lexeme, id) for id, lexeme in in_lexemes.iteritems())
        
    text_index = {}
    counter = 0
    for sentence in in_sentences:
        new_sentence = [word_ids[lexeme] for lexeme in sentence if lexeme in word_ids]
        if len(new_sentence):
            text_index[counter] = new_sentence
            counter += 1
    return text_index

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

def merge_constant_phrases(in_lexemes, in_text_index, in_constant_phrases):
    # modifying lexemes
    res_lexemes = copy.deepcopy(in_lexemes)
    for id_phrase in in_constant_phrases:
        word_phrase = [in_lexemes[id] for id in id_phrase]
        for id in id_phrase[1:]:
            res_lexemes.pop(id)
        res_lexemes[id_phrase[0]] = ' '.join(word_phrase)
    res_text = refresh_text_index(res_lexemes, in_text_index)
    return (res_lexemes, res_text)

def lexeme_associative_power(in_lexeme_id, in_text_index):
    # here area does not include the generative sentence (which the first appearance is in)
    adjacent_lexemes = set([])
    for sentence_id in in_text_index:
        if in_lexeme_id in in_text_index[sentence_id]:
            adjacent_lexemes.update(set(in_text_index[sentence_id]))
    # removing from the result the id of the target itself
    adjacent_lexemes.remove(in_lexeme_id)
    return len(adjacent_lexemes)

def extract_dominants(in_indexed_text, in_lexemes):
    powers = {lexeme_id: lexeme_associative_power(lexeme_id, in_indexed_text) \
        for lexeme_id in in_lexemes}
    unique_lexeme_powers = sorted(set(powers.values()))
    # maximal rank R corresponding to a lexeme group with the associative power of 2
    maximal_rank = len(unique_lexeme_powers)
    # see Chanyshev's papers
    critical_power = 0.5 * maximal_rank + 1
    dominants = [id for id in powers if powers[id] > critical_power]
    return dominants

class AssociativeModelBuilder(object):
    def __init__(self, in_text):
        # builds full_link_set and sentences
        self.initial_preprocessing(in_text)
        
        self.calculate_existence_areas()
        self.merge_constant_phrases()
        self.remove_attributive_lexemes()
        self.calculate_associative_power()
        self.remove_nondominants()
    
    # tokenizing, stopping, extracting full link set
    def initial_preprocessing(self, in_text):
        sentences = stop(tokenize_sentences(in_text))
        
        # raw words in the right order
        fls = link_lexemes.extract_full_link_set(sentences)
        self.active_lexemes = make_lexemes_dict(fls)
        
        # representing sentences as lists of FLS indices, not words themselves
        self.indexed_text = build_text_index(sentences, self.active_lexemes)
    
    def filter_constant_phrases(self):
        constant_phrases = extract_constant_phrases(self.existence_areas)
        (self.active_lexemes, self.sentences) = \
            merge_constant_phrases(self.active_lexemes, self.sentences, self.existence_areas)
        
        # rebuilding the affected structures
        self.calculate_existence_areas()
    
    def is_attributive_lexeme(self, in_id):
        # asymmetric difference of lists
        diff = lambda lhs, rhs: [elem for elem in lhs if elem not in rhs]
        
        target_area = set(self.existence_matrices[in_id])
        for id in self.active_lexemes:
            if not id == in_id:
                other_area = set(self.existence_matrices[id])
                if not len(target_area.difference(other_area)) \
                    and len(other_area.difference(target_area)):
                    return True
        return False
    
    def calculate_existence_areas(self):
        self.existence_areas = calculate_existence_areas(self.sentences, self.active_lexemes)

    def refresh_text_index(self):
        self.indexed_text = refresh_text_index(self.active_lexemes, self.indexed_text)

    def remove_attributive_lexemes(self):
        attributive_lexemes = [id for id in self.active_lexemes if self.is_attributive_lexeme(id)]
        for id in attributive_lexemes:
            self.active_lexemes.pop(id)
        
        # recalculating all the affected structures
        self.refresh_text_index()
        self.calculate_existence_areas()
    
    def calculate_associative_power(self):
        self.associative_power = {lexeme_id: lexeme_associative_power(lexeme_id, self.indexed_text) \
            for lexeme_id in self.active_lexemes}
    
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
    print stop(lexemes, in_filtering_set=filtering_set)

if __name__ == '__main__':
    test()
