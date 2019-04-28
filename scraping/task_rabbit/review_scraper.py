import sqlite3
import sys
from multiprocessing import Pool
from selenium import webdriver
import time


def load_database_taskers_no_reviews(conn):
    #Return taskers in database
    return [row[0] for row in conn.cursor().execute("SELECT tasker_id FROM taskers WHERE reviewed = 0").fetchall()]

def get_rating(el):
    second_class = el.get_attribute("class").split(" ")[1]
    if second_class == "ss-rkt-thumbup":
        return "positive"
    elif second_class == "ss-rkt-thumbdown":
        return "negative"
    else:
        "error"


def split_seq(seq, size):
    newseq = []
    splitsize = 1.0 / size * len(seq)
    for i in range(size):
        newseq.append(seq[int(round(i * splitsize)):int(round((i + 1) * splitsize))])
    return newseq

def store_tasker_data(review_data, conn, tasker_id):
    c = conn.cursor()
    c.executemany("INSERT INTO reviews(text, date, rating, tasker_id, service_title) "
              "VALUES(?,?,?,?,?)", [tuple(row) for row in review_data])
    c.execute("UPDATE taskers SET reviewed = 1 WHERE tasker_id = ?", (str(tasker_id),))
    conn.commit()


def scrape_reviews(taskers, db_name):
    conn = sqlite3.connect("../../databases/" + db_name)
    driver = webdriver.Chrome(executable_path=r'/usr/bin/chromedriver')
    for tasker in taskers:
        driver.get(base_url + str(tasker))
        new_url = driver.current_url
        review_data = []
        page = 1
        while True:
            driver.get(base_url + new_url.split("/")[-1] + "/reviews?review_page=" + str(page))
            time.sleep(2)
            reviews = driver.find_elements_by_css_selector(".profile-review")
            if reviews:
                review_data += [[
                            review.find_element_by_css_selector(".profile-review__message").text,
                            review.find_element_by_css_selector(".profile-review__meta").text,
                            get_rating(review.find_element_by_css_selector(".profile-review__rate")),
                            str(tasker),
                            review.find_element_by_css_selector(".profile-review__title").text[:-1]
                            ] for review in reviews]
                page += 1
            else:
                store_tasker_data(review_data, conn, tasker)
                break
    print ("Batch finished")
    conn.close()
    driver.close()


if __name__ == '__main__':

    num_threads = 5
    base_url = "https://www.taskrabbit.com/profile/"
    conn = sqlite3.connect("../../databases/" + sys.argv[1])
    non_reviewed_taskers = load_database_taskers_no_reviews(conn)
    conn.close()

    split_taskers = list(split_seq(non_reviewed_taskers, num_threads))
    print ("Scraping reviews in " + str(num_threads) + " batches...")
    print (split_taskers)
    with Pool(num_threads) as p:
        [p.apply_async(scrape_reviews, args=[tasker_list, sys.argv[1]]) for tasker_list in split_taskers]
        p.close()
        p.join()
