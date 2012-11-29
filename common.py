import nltk.corpus

DEFAULT_LANGUAGE = 'english'

# in_text is assumed to be a list of tokenized sentences
def stop(in_text, in_language = DEFAULT_LANGUAGE):
    filtering_set = nltk.corpus.stopwords.words(in_language)
    result = []
    for sentence in in_text:
        sentence_filtered = [word for word in sentence if word not in filtering_set]
        if len(sentence_filtered):
            result.append(sentence_filtered)
    return result
