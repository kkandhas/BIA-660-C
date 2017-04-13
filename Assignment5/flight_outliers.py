import datetime
import math
import time
import unicodedata

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dateutil import parser
from scipy.spatial import distance
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import MinMaxScaler, RobustScaler


def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])


def scrape_data(start_date, from_place, to_place, city_name):
    driver = webdriver.Chrome()
    driver.get('https://www.google.com/flights/explore/')
    time.sleep(0.1)
    from_input = driver.find_element_by_xpath('//*[@id="root"]/div[3]/div[3]/div/div[2]/div/div')

    from_input.click()
    actions = ActionChains(driver)
    actions.send_keys(from_place)
    actions.send_keys(Keys.ENTER)
    actions.perform()
    time.sleep(0.1)
    to_input = driver.find_element_by_xpath('//*[@id="root"]/div[3]/div[3]/div/div[4]/div/div')
    to_input.click()
    actions = ActionChains(driver)
    actions.send_keys(to_place)
    actions.send_keys(Keys.ENTER)
    actions.perform()
    time.sleep(0.1)

    url = driver.current_url
    new_url = url[:-10] + '{:%Y-%m-%d}'.format(start_date)
    driver.get(new_url)
    time.sleep(5)
    data = []
    results = driver.find_elements_by_class_name('LJTSM3-v-d')

    for result in results:
        driver.implicitly_wait(5)
        temp = result.find_element_by_class_name('LJTSM3-v-c').text.split(',')
        driver.implicitly_wait(1)
        if any(remove_accents(u"".join(city_name)).lower().title() in s for s in temp):
            bars = result.find_elements_by_class_name('LJTSM3-w-x')
            for bar in bars:
                ActionChains(driver).move_to_element(bar).perform()
                time.sleep(0.01)
                price = result.find_element_by_class_name('LJTSM3-w-k').find_elements_by_tag_name('div')[0].text
                tmp = result.find_element_by_class_name('LJTSM3-w-k').find_elements_by_tag_name('div')[1].text
                tmp1 = tmp.split('-')
                datfl = tmp1[0]
                data.append([datfl, price])

    return pd.DataFrame(data, columns=['Date_of_Flight', 'Price'])


def scrape_data_90(start_date, from_place, to_place, city_name):
    driver = webdriver.Chrome()
    driver.get('https://www.google.com/flights/explore/')
    time.sleep(0.1)
    from_input = driver.find_element_by_xpath('//*[@id="root"]/div[3]/div[3]/div/div[2]/div/div')

    from_input.click()
    actions = ActionChains(driver)
    actions.send_keys(from_place)
    actions.send_keys(Keys.ENTER)
    actions.perform()
    time.sleep(0.1)
    to_input = driver.find_element_by_xpath('//*[@id="root"]/div[3]/div[3]/div/div[4]/div/div')
    to_input.click()
    actions = ActionChains(driver)
    actions.send_keys(to_place)
    actions.send_keys(Keys.ENTER)
    actions.perform()
    time.sleep(0.1)

    url = driver.current_url
    new_url = url[:-10] + '{:%Y-%m-%d}'.format(start_date)
    driver.get(new_url)
    time.sleep(5)
    data = []
    results = driver.find_elements_by_class_name('LJTSM3-v-d')

    for result in results:
        driver.implicitly_wait(5)
        temp = result.find_element_by_class_name('LJTSM3-v-c').text.split(',')
        driver.implicitly_wait(1)
        if any(remove_accents(u"".join(city_name)).lower().title() in s for s in temp):
            bars = result.find_elements_by_class_name('LJTSM3-w-x')
            for bar in bars:
                ActionChains(driver).move_to_element(bar).perform()
                time.sleep(0.01)
                price = result.find_element_by_class_name('LJTSM3-w-k').find_elements_by_tag_name('div')[0].text
                tmp = result.find_element_by_class_name('LJTSM3-w-k').find_elements_by_tag_name('div')[1].text
                tmp1 = tmp.split('-')
                datfl = tmp1[0]
                data.append([datfl, price])
    df1 = pd.DataFrame(data, columns=['Date_of_Flight', 'Price'])
    data2 = []

    next_b = driver.find_element_by_xpath(
        '//*[@id="root"]/div[3]/div[4]/div/div[2]/div[1]/div/div[2]/div[2]/div/div[2]/div[5]/div')
    next_b.click()

    time.sleep(5)

    results = driver.find_elements_by_class_name('LJTSM3-v-d')

    for result in results:
        driver.implicitly_wait(5)
        temp = result.find_element_by_class_name('LJTSM3-v-c').text.split(',')
        driver.implicitly_wait(1)
        if any(remove_accents(u"".join(city_name)).lower().title() in s for s in temp):
            bars = result.find_elements_by_class_name('LJTSM3-w-x')
            i = 0
            for bar in bars:
                ActionChains(driver).move_to_element(bar).perform()
                time.sleep(0.01)
                i += 1
                if i > 30:
                    price = result.find_element_by_class_name('LJTSM3-w-k').find_elements_by_tag_name('div')[0].text
                    tmp = result.find_element_by_class_name('LJTSM3-w-k').find_elements_by_tag_name('div')[1].text
                    tmp1 = tmp.split('-')
                    datfl = tmp1[0]
                    data2.append([datfl, price])
    df2 = pd.DataFrame(data2, columns=['Date_of_Flight', 'Price'])
    df3 = df1.append(df2, ignore_index=True)
    return df3


# TASK 3
def clean_data(flight_data):
    dt = flight_data
    # cleaning the Price colm
    for i, x in enumerate(dt['Price']):
        val = x.replace(',', '').strip('$')

        dt['Price'][i] = int(val)
    # cleaning date_of_flight
    tmp = parser.parse(dt['Date_of_Flight'][0])
    for i, x in enumerate(dt['Date_of_Flight']):
        dt['Date_of_Flight'][i] = parser.parse(x)
        dt['Date_of_Flight'][i] = (dt['Date_of_Flight'][i] - tmp).days
    return dt


# df = df.set_value(49, 'Price', 255)
def variance(mylist):
    mylen = len(mylist)
    mymean = sum(mylist) / mylen

    temp = 0

    for i in range(mylen):
        temp += (mylist[i] - mymean) * (mylist[i] - mymean)
    return temp / mylen


def std_dev(mylist):
    return math.sqrt(variance(mylist))


def makeX(days, prices):
    return np.concatenate([days, prices], axis=1)


def task_3_dbscan(flight_data):
    dtemp = flight_data.copy()
    dtmp = clean_data(dtemp)
    # X = StandardScaler().fit_transform(dtmp[['Date_of_Flight', 'Price']])
    # X = MaxAbsScaler().fit_transform(dtmp[['Date_of_Flight', 'Price']])
    # XP = RobustScaler().fit_transform(dtmp[['Date_of_Flight', 'Price']])
    # '''
    prs = dtmp['Price']
    dts = dtmp['Date_of_Flight']

    XP = RobustScaler().fit_transform(prs[:, None])
    # XP = MinMaxScaler(feature_range=(-3,3)).fit_transform(prs[:,None])
    days = MinMaxScaler(feature_range=(-3, 3)).fit_transform(dts[:, None])
    X = makeX(days, XP)
    # '''
    db = DBSCAN(eps=.3, min_samples=4).fit(X)

    labels = db.labels_
    clusters = len(set(labels))
    unique_labels = set(labels)
    colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))

    plt.subplots(figsize=(12, 12))
    cord = []

    for k, c in zip(unique_labels, colors):
        class_member_mask = (labels == k)
        xy = X[class_member_mask]
        cord.append(xy)
        plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=c, markeredgecolor='k', markersize=10)
    plt.savefig('task_3_dbscan.png')
    #for index, xy in enumerate(zip(days, XP)):
    #    plt.annotate('{}: ({:0.2f}, {:0.2f})'.format(index, xy[0][0], xy[1][0]), xytext=(xy[0] - 0.25, xy[1] - 0.1),
    #                xy=xy)

    plt.title("Total Clusters: {}".format(clusters), fontsize=14, y=1.01)
    dtmp['dbscan_labels'] = db.labels_

    clstrs = [(dtmp['dbscan_labels'] == i) for i in xrange(clusters)]
    outliers = dtmp['dbscan_labels'] == -1
    outlier_index = []
    for i, x in enumerate(outliers):
        if x == True:
            outlier_index.append(i)

    clster_index = []
    for y, z in enumerate(clstrs):
        temp_index = []
        for i, x in enumerate(z):
            if x == True:
                temp_index.append(i)
        clster_index.append(temp_index)

    n = len(clstrs)
    outl_data = []
    outl_data_index = []

    dis_mean = []
    for i, x in enumerate(clstrs):
        if i != (n - 1):
            dis_mean.append(cord[i].mean(axis=0))
    Y = distance.cdist(cord[n - 1], dis_mean, 'euclidean')

    for j, y in enumerate(outlier_index):
        minn = Y[j].min()
        close_clstr = []
        for i, x in enumerate(Y[j]):
            if x == minn:
                flag = i
        for x in clster_index[flag]:
            close_clstr.append(dtmp['Price'][x])

        mean = sum(close_clstr) / len(close_clstr)
        std = std_dev(close_clstr)
        # checking conditions
        if (dtmp['Price'][y] < (mean - (2 * std))) and (dtmp['Price'][y] < (mean - 50)):
            outl_data_index.append(y)
    for x in outl_data_index:
        outl_data.append([flight_data['Date_of_Flight'][x], flight_data['Price'][x]])

    return pd.DataFrame(outl_data, columns=['Date_of_Flight', 'Price'])


def task_3_IQR(flight_data):
    fl_data = clean_data(flight_data)
    ds = fl_data.sort_values(by='Price')

    ds['Price'].plot.box()
    plt.savefig('task_3_IQR.png')

    Q1 = ds['Price'].quantile(0.25)
    Q3 = ds['Price'].quantile(0.75)
    IQR = Q3 - Q1

    outl_index = []
    outl_data = []

    for i, x in enumerate(fl_data['Price']):
        if (x < abs(Q1 - (1.5 * IQR))) or (x > abs(Q3 + (1.5 * IQR))):
            outl_index.append(i)

    for x in outl_index:
        outl_data.append([ds['Date_of_Flight'][x], ds['Price'][x]])

    return pd.DataFrame(outl_data, columns=['Date_of_Flight', 'Price'])


# def task_3_ec(flight_data):


def task_4_dbscan(flight_data):
    dtemp = flight_data.copy()
    dtmp = clean_data(dtemp)
    # X = StandardScaler().fit_transform(dtmp[['Date_of_Flight', 'Price']])
    # X = MaxAbsScaler().fit_transform(dtmp[['Date_of_Flight', 'Price']])
    # X = RobustScaler().fit_transform(dtmp[['Date_of_Flight', 'Price']])
    # '''
    prs = dtmp['Price']
    dts = dtmp['Date_of_Flight']

    XP = RobustScaler().fit_transform(prs[:, None])
    # XP = MinMaxScaler(feature_range=(-3,3)).fit_transform(prs[:,None])
    days = MinMaxScaler(feature_range=(-3, 3)).fit_transform(dts[:, None])

    X = makeX(days, XP)
    # '''
    db = DBSCAN(eps=.35, min_samples=5).fit(X)

    labels = db.labels_
    clusters = len(set(labels))
    unique_labels = set(labels)
    colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))

    plt.subplots(figsize=(12, 8))
    cord = []

    for k, c in zip(unique_labels, colors):
        class_member_mask = (labels == k)
        xy = X[class_member_mask]
        cord.append(xy)
        plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=c, markeredgecolor='k', markersize=10)

    plt.title("Total Clusters: {}".format(clusters), fontsize=14, y=1.01)
    dtmp['dbscan_labels'] = db.labels_
    # plt.savefig('task_3_dbscan.png')

    clstrs = [(dtmp['dbscan_labels'] == i) for i in xrange(clusters)]
    outliers = dtmp['dbscan_labels'] == -1
    outlier_index = []
    for i, x in enumerate(outliers):
        if x == True:
            outlier_index.append(i)

    clster_index = []
    for y, z in enumerate(clstrs):
        temp_index = []
        for i, x in enumerate(z):
            if x == True:
                temp_index.append(i)
        clster_index.append(temp_index)

    n = len(clstrs)

    outl_data = []
    outl_data_index = []

    min_mean = 10000
    avg_clstr_min = 10000
    clstr_price = []
    for i, x in enumerate(clster_index):
        temp_index = []
        if i != (n - 1):
            for j in x:
                temp_index.append(dtmp['Price'][j])
            clstr_price.append(temp_index)

    flag = None
    best_clpr_i = []
    best_clster_index = None
    for j, y in enumerate(clstr_price):
        for i, x in enumerate(y):

            if i == (len(y) - 5):
                break

            minn = min(y[i:i + 5])
            maxx = max(y[i:i + 5])
            if (maxx - minn) <= 20:
                temp_best_prices = y[i:i + 5]
            else:
                continue

            mean = sum(temp_best_prices) / len(temp_best_prices)
            if mean < min_mean:
                min_mean = mean
                flag = i
        if flag is not None:
            best_clpr_i = y[flag:flag + 5]
            best_clpr_mean = sum(best_clpr_i) / len(best_clpr_i)
            if best_clpr_mean < avg_clstr_min:
                avg_clstr_min = best_clpr_mean
                best_clster_index = j

    print "Best Price Period :"

    outl_data_index = clster_index[best_clster_index][flag:flag + 5]
    for x in outl_data_index:
        outl_data.append([flight_data['Date_of_Flight'][x], flight_data['Price'][x]])

    return pd.DataFrame(outl_data, columns=['Date_of_Flight', 'Price'])


# Task 3-1 Testing
dk = scrape_data_90(datetime.datetime(2017, 5, 3, 0, 0), 'new york', 'Australia', 'Sydney')
dj = dk.copy()

# dj['Price'][64] = '$1366'
dfin = task_3_dbscan(dj)

print "Task 3-1 Output:"
print dfin

# Task 3-2 Testing
dl = scrape_data_90(datetime.datetime(2017, 5, 3, 0, 0), 'new york', 'India', 'chennai')
dj = dl.copy()
'''
dj['Price'][64] = '$1655'
dj['Price'][74] = '$2055'
dj['Price'][44] = '$655'
dj['Price'][54] = '$55'
#'''

dfin2 = task_3_IQR(dj)

print "Task 3-2 Output:"
print dfin2

# Task 4 Testing:
dj = dl.copy()
print "Task 4 Output:"
dfin3 = task_4_dbscan(dj)

print dfin3
