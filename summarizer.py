from nltk.stem import PorterStemmer, SnowballStemmer
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from nltk.tokenize import sent_tokenize, wordpunct_tokenize, word_tokenize
from nltk.corpus import stopwords

import json
import math

OUTPUT_FILE = "summarizer.html"


# Method to print the top words from LDA
def print_top_words(model, feature_names, n_top_words, word_order_dict):
    features = list()

    # Preserve the order of words in the sentence
    for feature in feature_names:
        # Get each of the top words from LDA and convert to normal format
        feature = feature.encode('ascii', 'ignore')
        for idx, wrd in word_order_dict.iteritems():
            # compare with each word in word_order_dict dictionary. If there is a match, store the index
            if feature == wrd:
                features.append(idx)
    # Sort the indices to get the correct order of words in the sentence
    features.sort()
    return " ".join([word_order_dict[i] for i in features])

    # for topic_idx, topic in enumerate(model.components_):
        # print("Topic #%d:" % topic_idx)
        # for i in topic.argsort()[:-n_top_words - 1:-1]:
        #     features.append(i)
        # return (" ".join([feature_names[i]
        #                 for i in features]))


if __name__ == '__main__':
    with open('data.json') as data_file:
        data = json.load(data_file)

    # stemmer = PorterStemmer()                 # You can change the stemmer here. Though I haven't used it
    lemmatizer = WordNetLemmatizer()            # Lemmatizer which shortens the words. e.g.) causes -> cause
    # vectorizer = TfidfVectorizer()              # Creates vectors of each word
    vectorizer = CountVectorizer()

    # Used for LDA. Play around with n_topics and max_iter
    lda = LatentDirichletAllocation(n_topics=1, max_iter=10, learning_method='online', learning_offset=50.,
                                    random_state=0)
    # List to store the lemmatized words
    lemmatized_words = list()

    write_output = open(OUTPUT_FILE, 'w')
    write_output.write('<html><head><title>Text Summary</title></head> <body><table border="1">')

    # Create train and test data split - 80% train and 20% test data
    train_data = data[0:int(len(data)*0.8)]
    test_data = data[int(len(data)*0.8):]

    for line in train_data:
        # Dictionary to store the order of words
        word_order_dict = dict()
        count = 0
        # Changed from unicode to string
        normal_words = line["content"].encode('ascii', 'ignore')

        # Used word tokenizer to tokenize the words
        tokens = word_tokenize(normal_words)
        for token in tokens:
            token = token.lower()
            # stemmed_words.append(stemmer.stem(token))
            # Used lemmatizer on the words
            lemmatized_words.append(lemmatizer.lemmatize(token))
            word_order_dict[count] = lemmatizer.lemmatize(token)
            count += 1

        # Removed stop words
        lemmatized_words = [word for word in lemmatized_words if word not in stopwords.words('english')]

        # Perform LDA if there are any words that are lemmatized. Skip if the content is blank
        if len(lemmatized_words) > 1:
            # Create a vector of each word. It will be used to perform LDA
            vectors = vectorizer.fit_transform(lemmatized_words)

            # Perform LDA on these word vectors
            lda.fit(vectors)

            # Get the top words after performing LDA
            tf_feature_names = vectorizer.get_feature_names()


            # Print the top 10 words (if there are more than 10 words). Write output in HTML file
            write_output.write('<tr><th>' + str(line["index"]) + '</th><td>' +
                               print_top_words(lda, tf_feature_names, 100, word_order_dict) + '</td></tr>')

        lemmatized_words = list()

    write_output.write('</table></body></html')
    write_output.close()