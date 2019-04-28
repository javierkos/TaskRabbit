import sqlite3
from analysis.regression.data_prep import DataPreparation
import pandas as pd
import matplotlib
matplotlib.use
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from scipy.stats import shapiro
from scipy.stats import anderson
from scipy.stats import normaltest
from scipy.stats import kstest
import statsmodels.stats.api as sms
from statsmodels.compat import lzip
#from analysis.regression.regression_dictsservice_regression_dicts import default_init_steps, service_steps
from analysis.regression.data_prep import DataPreparation
from sklearn.feature_selection import SelectKBest, f_regression
import numpy as np
import itertools
import math

dct = {}

conn = sqlite3.connect("../databases/taskrabbit_ny.db")

c = conn.cursor()

data_prep = DataPreparation()

vars_important = {}

services = {
    1: ["avg_mood", "avg_vehicles", "per_white"],
    2: ["per_male", "errors_per_word", "avg_sent_desc"],
    3: ["per_male", "per_white", "errors_per_word", "avg_vehicles"],
    4: ["per_white", "avg_sent_desc", "avg_vehicles"],
    6: ["per_male", "avg_mood", "errors_per_word", "avg_vehicles"],
    7: ["per_white", "avg_mood", "errors_per_word", "avg_vehicles"],
    8: ["per_white", "avg_mood", "avg_vehicles"],
    29: ["per_white", "avg_vehicles"],
    30: ["avg_mood", "errors_per_word", "avg_sent_desc"],
    35: ["per_male", "avg_mood"],
    51: ["per_male", "per_white", "errors_per_word"],
    52: ["per_male", "per_white", "avg_mood", "avg_sent_desc", "avg_vehicles"]

}


def mallow_cp(model, s2, N):
    return (model["result"].ssr / s2) - N + model["num_vars"] * 2

def plot_mallows(models):
    x, y = [], []
    fig1, ax1 = plt.subplots()
    fig1.set_size_inches(10, 10)
    for k in models:
        for model in models[k]:
            x.append(k)
            y.append(model["mallows"])
    plt.scatter(x, y, alpha=0.60, color=(.2, .5, .8))
    ax1.set_xlabel('Number of predictors', fontsize=18)
    ax1.set_ylabel("Mallow's Cp", fontsize=18)
    ax1.set_ylim([0, 10])
    x = np.linspace(*ax1.get_xlim())
    ax1.plot(x, x, color=(.2, .5, .8), alpha=0.8)

    # removing top and right borders
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    ax1.patch.set_alpha(0.7)

    ax1.xaxis.set_ticks_position('none')
    ax1.yaxis.set_ticks_position('none')

    # adds major gridlines
    ax1.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.5)
    ax1.spines['right'].set_color((.8, .8, .8))
    ax1.spines['top'].set_color((.8, .8, .8))
    ax1.grid('on', linestyle='dotted')
    ax1.tick_params(axis='both', which='major', labelsize=15)
    ax1.tick_params(axis='both', which='minor', labelsize=15)

    plt.savefig("scatter_mallows.png")
    plt.show()


def get_all_subsets(X, y, mallows=True):
    combs = []
    results = []
    for i in range(1, len(X) + 1):
        els = [list(x) for x in itertools.combinations(X, i)]
        combs.extend(els)
    for comb in combs:
        model = sm.OLS(y, sm.add_constant(X[list(comb)]))
        result = model.fit()
        results.append({"model": model, "result": result, "num_vars": len(comb), "vars": X[list(comb)]})

    full_mse_res = sm.OLS(y, sm.add_constant(X)).fit().mse_resid
    acceptable_models = {}

    for model in results:
        not_acceptable = False
        for pvalue in model["result"].pvalues:
            if pvalue > 0.05:
                not_acceptable = True
                break
        if not_acceptable:
            continue

        mallows_objective = model["num_vars"]
        curr_mallows = mallow_cp(model, full_mse_res, X.shape[0])
        curr_min = None
        if model["num_vars"] in acceptable_models and len(acceptable_models[model["num_vars"]]) > 9:
            curr_min = acceptable_models[model["num_vars"]][-1]["mallows"]

        model["mallows"] = curr_mallows
        model["mallows_diff"] = abs(curr_mallows - mallows_objective)
        if not curr_min is None:
            if model["mallows_diff"] < abs(curr_min - mallows_objective):
                del acceptable_models[model["num_vars"]][-1]
                acceptable_models[model["num_vars"]].append(model)
            else:
                continue
        else:
            if not model["num_vars"] in acceptable_models:
                acceptable_models[model["num_vars"]] = []
            acceptable_models[model["num_vars"]].append(model)

        acceptable_models[model["num_vars"]] = \
            sorted(acceptable_models[model["num_vars"]], key=lambda k: k['mallows_diff'])

    curr_best = None
    for num_vars in acceptable_models:
        for model in acceptable_models[num_vars]:

            if curr_best is None:
                curr_best = model
            else:
                if curr_best["mallows_diff"] > model["mallows_diff"]:
                    curr_best = model

    print(curr_best["result"].summary())
    std = curr_best["model"].exog.std(0)
    std[0] = 1
    tt = curr_best["result"].t_test(np.diag(std))
    print(tt.summary())
    tt.summary_frame()

    fig = plt.figure(figsize=(12, 30))
    sm.graphics.plot_partregress_grid(curr_best["result"])
    plt.savefig("resid_ny.png")
    #plt.show()
    if False:
        fig, ax = plt.subplots(2, 2, sharex='col', sharey='row', figsize=(12, 10))
        params = list(dict(curr_best["result"].params).keys())

        n1 = math.floor(len(params)/2)
        n2 = math.floor(len(params) % 2)

        for i in range(2):
            for j in range(2):
                try:
                    ax[i, j].scatter(curr_best["result"].model.exog[:, i * 2 + j ], curr_best["result"].resid)
                    ax[i, j].set_xlabel(params[i*2 + j])
                    ax[i, j].set_ylabel("resid")
                    ax[i, j].axhline(y=0, color="black")
                except Exception:
                    break
        plt.savefig("resid_sf.png")
        plt.show()
        #fig = plt.figure(figsize=(12, 10))
        #fig = sm.graphics.plot_regress_exog(curr_best["result"], "per_white", fig=fig)
        fig = sm.graphics.plot_partregress_grid(curr_best["result"], fig=fig)
        fig.gca().set_title("")
        plt.suptitle("")
        plt.savefig("resid_ny.png")
        #plt.show()

    stat, p = shapiro(curr_best["result"].resid)
    print ("Shapiro")
    print('Statistics=%.3f, p=%.3f' % (stat, p))
    stat, p = normaltest(curr_best["result"].resid)
    print ("D’Agostino’s")
    print('Statistics=%.3f, p=%.3f' % (stat, p))

    stat, p = kstest(curr_best["result"].resid, 'norm')
    print("Kolmogorov-Smirnov")
    print('Statistics=%.3f, p=%.3f' % (stat, p))
    #plot_mallows(acceptable_models)
    return curr_best["result"].rsquared_adj

    for var in curr_best["vars"]:
        coef = curr_best["result"].params[var]
        pos_neg = "pos"
        if coef < 0:
            pos_neg = "neg"
        try:
            dct[var + "_" + pos_neg] += 1
        except Exception:
            dct[var + "_" + pos_neg] = 1


adjusted_r2s = {}
    # exit()
for service in services.keys():
    #### COMBINATION #####
    print (service)
    rows = []
    for row in c.execute("SELECT * FROM service_location_data WHERE service_id = " + str(service)):
        rows.append((row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
    X = pd.DataFrame(rows, columns=["per_male", "per_white", "avg_mood", "errors_per_word", "avg_sent_desc", "avg_vehicles", "med_price"])
    y = X["med_price"]
    X = X.drop(["med_price"], axis=1)


    X_data_geog = data_prep.data_load("new_york", c.execute("SELECT name FROM services WHERE service_id = " + str(service)).fetchall()[0][0], True)
    #y = X_data_geog["Median service cost"]
    X_data_geog = X_data_geog.drop(["Median service cost"], axis=1)
    #print (X_data_geog)


    X = pd.concat([X.reset_index(drop=True), X_data_geog.reset_index(drop=True)], axis=1)


    X = data_prep.scale_data(X)
    X = X[~X.isin([np.nan, np.inf, -np.inf]).any(1)]
    print (X)
    X = data_prep.calculate_vif_(X, 10)

    try:
        adjusted_r2s[service] = get_all_subsets(X, y)
    except Exception as e:
        print (e)
        pass
    #### ONLY TASKRABBIT
    '''
    print (service)

    rows = []
    for row in c.execute("SELECT * FROM service_location_data WHERE service_id = " + str(service)):
        rows.append((row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
    X = pd.DataFrame(rows, columns=["per_male", "per_white", "avg_mood", "errors_per_word", "avg_sent_desc", "avg_vehicles", "med_price"])
    y = X["med_price"]
    X = X.drop(["med_price"], axis=1)


    X = data_prep.scale_data(X)
    X = data_prep.calculate_vif_(X, 10)

    try:
        adjusted_r2s[service] = get_all_subsets(X, y)

    except Exception as e:
        print (e)
        pass

    '''
    #### ONLY CENSUS #####
    '''
    print (service)

    X_data_geog = data_prep.data_load("san_francisco", c.execute("SELECT name FROM services WHERE service_id = " + str(service)).fetchall()[0][0], True)
    y = X_data_geog["Median service cost"]
    X_data_geog = X_data_geog.drop(["Median service cost"], axis=1)
    #print (X_data_geog)


    X = data_prep.scale_data(X_data_geog)
    X = data_prep.calculate_vif_(X, 10)

    try:
        adjusted_r2s[service] = get_all_subsets(X, y)
    except Exception as e:
        print (e)
        pass
    '''



print (vars_important)
print (adjusted_r2s)


