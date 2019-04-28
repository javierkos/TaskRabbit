import sqlite3
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
import re

regex = re.compile('[^a-zA-Z]')
conn = sqlite3.connect('../databases/taskrabbit_los_angeles.db')
c = conn.cursor()

labels = []
texts = []
c.execute("SELECT text,rating FROM reviews;")
i = 0
for row in c:
    lab = row[1]
    if lab == "positive":
        if i == 50:
            i = 0
            labels.append(lab)
            texts.append(' '.join([word for word in row[0].split() if word.isalpha()]))
        i += 1
    else:
        labels.append(lab)
        texts.append(' '.join([word for word in row[0].split() if word.isalpha()]))

count_vect = CountVectorizer()
X_train_counts = count_vect.fit_transform(texts)
tfidf_transformer = TfidfTransformer()
X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
clf = MultinomialNB().fit(X_train_tfidf, labels)

test = count_vect.transform(["Suck sucked not bad terrible horrible "])
print (clf.predict(test))

def most_informative_feature_for_binary_classification(vectorizer, classifier, n=10):
    class_labels = classifier.classes_
    feature_names = vectorizer.get_feature_names()
    topn_class1 = sorted(zip(classifier.coef_[0], feature_names))[:n]
    topn_class2 = sorted(zip(classifier.coef_[0], feature_names))[-n:]

    for coef, feat in topn_class1:
        print (class_labels[0], coef, feat)

    for coef, feat in reversed(topn_class2):
        print (class_labels[1], coef, feat)

most_informative_feature_for_binary_classification(count_vect, clf, 30)