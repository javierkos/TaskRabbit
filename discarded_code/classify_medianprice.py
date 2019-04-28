import sqlite3
import numpy as np
import sys
import matplotlib
matplotlib.use
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import SGDRegressor, Ridge
from utils import get_project_root
import nltk
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from sklearn.svm import SVR

if __name__ == '__main__':
    matplotlib.rcParams['mathtext.fontset'] = 'custom'
    matplotlib.rcParams['mathtext.rm'] = 'Bitstream Vera Sans'
    matplotlib.rcParams['mathtext.it'] = 'Bitstream Vera Sans:italic'
    matplotlib.rcParams['mathtext.bf'] = 'Bitstream Vera Sans:bold'
    matplotlib.pyplot.title(r'ABC123 vs $\mathrm{ABC123}^{123}$')
    
    stop_words = set(stopwords.words('english'))
    conn = sqlite3.connect('databases/taskrabbit_los_angeles.db')
    conn2 = sqlite3.connect('databases/taskrabbit_ny.db')
    conn3 = sqlite3.connect('databases/taskrabbit_san_francisco.db')
    c = conn.cursor()
    c2 = conn2.cursor()
    c3 = conn3.cursor()

    prices = []
    texts = []
    c.execute("SELECT DISTINCT descriptions.text, price_details.amount FROM price_details, descriptions WHERE  price_details.tasker_id = descriptions.tasker_id AND price_details.service_id = 1 ORDER BY amount DESC;")
    i = 0
    for row in c:
        texts.append(' '.join([word for word in row[0].split() if word.isalpha()]))
        prices.append(float(row[1]))

    c2.execute("SELECT DISTINCT descriptions.text, price_details.amount FROM price_details, descriptions WHERE  price_details.tasker_id = descriptions.tasker_id AND price_details.service_id = 1 ORDER BY amount DESC;")
    i = 0
    for row in c2:
        texts.append(' '.join([word for word in row[0].split() if word.isalpha()]))
        prices.append(float(row[1]))

    c3.execute("SELECT DISTINCT descriptions.text, price_details.amount FROM price_details, descriptions WHERE  price_details.tasker_id = descriptions.tasker_id AND price_details.service_id = 1 ORDER BY amount DESC;")
    i = 0
    for row in c3:
        texts.append(' '.join([word for word in row[0].split() if word.isalpha()]))
        prices.append(float(row[1]))



    print (len(prices))
    count_vect = CountVectorizer()
    X_train_counts = count_vect.fit_transform(texts)
    tfidf_transformer = TfidfTransformer()
    X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)

    X_train, X_test, y_train, y_test = train_test_split(X_train_tfidf, prices, test_size=0.15, random_state = 42)

    clf = Ridge(alpha=1.0).fit(X_train, y_train)
    print(clf.score(X_test, y_test))

    #clf = SGDRegressor(max_iter=5000, tol=1e-5).fit(X_train_tfidf, prices)
    clf = Ridge(alpha=1.0).fit(X_train_tfidf, prices)

    print (clf.score(X_train_tfidf, prices))


    most_inf = clf.coef_.argsort()[-10:][::-1]
    least_inf = clf.coef_.argsort()[:10][::-1]

    labels = [count_vect.get_feature_names()[index] for index in most_inf]
    coeffs = [clf.coef_[index] for index in most_inf]

    labels += [count_vect.get_feature_names()[index] for index in least_inf]
    coeffs += [clf.coef_[index] for index in least_inf]


    print ("Most positive features:")
    print ([count_vect.get_feature_names()[index] for index in most_inf])

    print ("Least positive features:")
    print ([count_vect.get_feature_names()[index] for index in least_inf])

    coeffs = np.array(coeffs)
    labels = np.array(labels)
    mask_lower = coeffs < 0
    mask_higher = coeffs >= 0

    fig, ax = plt.subplots()
    plt.bar(labels[mask_higher], coeffs[mask_higher], color="#1696d2")
    plt.bar(labels[mask_lower], coeffs[mask_lower], color="#fdbf11")
    plt.xticks(rotation=25)
    fig.set_size_inches(18, 18)
    fig.savefig('desc.png')
    plt.show()



'''
feature_array = np.array(X_train_tfidf.get_feature_names())
tfidf_sorting = np.argsort(response.toarray()).flatten()[::-1]

n = 3
top_n = feature_array[tfidf_sorting][:n]
'''
