import matplotlib
import importlib
import sys
import itertools
matplotlib.use
import time
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import statsmodels.api as sm
#from analysis.regression.regression_dictsservice_regression_dicts import default_init_steps, service_steps
from analysis.regression.data_prep import DataPreparation
from sklearn.feature_selection import SelectKBest, f_regression
import numpy as np
'''
    Takes one parameter which is the name (key) of the city - eg: ny, san_francisco etc.
'''

dct = {}
font = {'family' : 'normal',
        'weight': 'normal',
        'size'   : 11}

matplotlib.rc('font', **font)
class RegressionWrapper:

    def __init__(self, city_name):
        self.city_name = city_name
        self.data_prep = DataPreparation()
        self.overall_data = []

    def run_dicts(self, set_up_dict, regression_dict):
        r2 = {}
        adjusted_r2 = {}
        self.objects = tuple(service for service in regression_dict.keys())
        self.data = None
        for service in regression_dict.keys():
            print (service)
            for step in set_up_dict.keys():
                if step == "load":
                    X_data = self.data_prep.data_load(self.city_name, service)
                    #X_data = X_data.drop("Av. desc. sentiment", 1)
                elif step == 'store_map':
                    self.data_prep.plot_heatmap(X_data, service)
                elif step == 'overall_data':
                    if self.data is None:
                        vars = list(X_data)[:-1]
                        self.data = {var: [] for var in vars}
                    print(self.data)
                    print (X_data.shape)
                    #X_data["Median household income"] = pd.to_numeric(X_data["Median household income"])
                    correlations = X_data.corr(method="spearman")["Median service cost"]
                    print (correlations)
                    for var in self.data.keys():
                        self.data[var].append(correlations[var])
                elif step == 'init':
                    print("\nSplitting target from input variables...")
                    X, y = self.data_prep.split_target(X_data)
                elif step == 'vif':
                    keep = X[set_up_dict[step]['keep']]
                    threshold = set_up_dict[step]['threshold']
                    print("\nCalculating vif and dropping variables over threshold " + str(threshold) + "...")
                    X = self.data_prep.calculate_vif_(X, threshold)
                    X = pd.concat([X, keep], axis=1)
            for step in regression_dict[service].keys():
                print (step)
                if step == 'vif':
                    threshold = regression_dict[service][step]['threshold']
                    print("\nCalculating vif and dropping variables over threshold " + str(threshold) + "...")

                    X = self.data_prep.calculate_vif_(X, threshold)
                elif step == 'leave':
                    X = X[regression_dict[service][step]]
                elif step == 'remove':
                    for var in regression_dict[service][step]['vars']: X = X.drop(var, 1)
                elif step == 'select_best':
                    selector = SelectKBest(f_regression, k=regression_dict[service][step]['k'])
                    selector.fit(X, y)
                    X_new = selector.transform(X)
                    mask = selector.get_support()
                    print (mask)
                    new_features = X.columns[mask]
                    X = pd.DataFrame(X_new, columns = new_features)
                    print (new_features)
                elif step == 'scale':
                    print("\nScaling input variables...")
                    X = self.data_prep.scale_data(X)
                elif step == 'all_subsets':
                    get_all_subsets(X, y)
                elif step == 'fit':
                    print (list(X.columns.values))
                    print("\nFitting linear regression model...")
                    est = sm.OLS(y, sm.add_constant(X.values))
                    est2 = est.fit()
                    r2[service] = est2.rsquared
                    adjusted_r2[service] = est2.rsquared_adj
                    cols = ["Const"] + list(X.columns.values)
                    print("\n\n")
                    print(est2.summary(xname=cols))
                elif step == 'leave_just':
                    X = X[regression_dict[service][step]["vars"]]
                elif step == 'stepwise':
                    new_cols = stepwise_selection(X, y)
                    X = X[new_cols]
                elif step == 'plots':
                    continue

                    for i,col in enumerate(cols[1:]):                 
                        fig, ax = plt.subplots()
                        fig = sm.graphics.plot_fit(est2, i + 1, ax=ax)
                        ax.set_ylabel("Median price")
                        ax.set_xlabel(col)
                        ax.set_title("Linear Regression")
                        plt.show()
        self.objects = [obj if len(obj) < 15 else obj[:12] + "..." for obj in self.objects]
        for var in self.data.keys():
            fig, ax = plt.subplots()
            plt.bar(np.arange(len(self.objects)), self.data[var], align='center', alpha=1)
            plt.xticks(np.arange(len(self.objects)), self.objects)
            plt.xticks(rotation=25)
            fig.set_size_inches(16, 12)
            
            plt.ylabel('Usage')
            plt.title('Kendall Correlation between ' + var + " and median price")
            plt.show()
        print (r2)
        print (adjusted_r2)

def mallow_cp(model, s2, N):
    return (model["result"].ssr/s2) - N + model["num_vars"]*2

def plot_mallows(models):
    x, y = [], []
    fig1, ax1 = plt.subplots()
    fig1.set_size_inches(10, 10)
    for k in models:
        for model in models[k]:
            x.append(k)
            y.append(model["mallows"])
    plt.scatter(x, y, alpha=0.70, color="#3fc380")
    ax1.set_xlabel('Number of predictors', fontsize=12)
    ax1.set_ylabel("Mallow's Cp", fontsize=12)
    ax1.set_ylim([0, 10])
    x = np.linspace(*ax1.get_xlim())
    ax1.plot(x, x, color="#3fc380")

    # removing top and right borders
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)

    ax1.patch.set_alpha(0.5)

    ax1.xaxis.set_ticks_position('none')
    ax1.yaxis.set_ticks_position('none')

    # adds major gridlines
    ax1.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.5)
    plt.savefig("scatter_mallows.png")
    plt.show()

        


def get_all_subsets(X, y):
    combs = []
    results = []

    # Find all possible combination models, and fit them with our data
    for i in range(1, len(X) + 1):
        els = [list(x) for x in itertools.combinations(X, i)]
        combs.extend(els)
    for comb in combs:
        model = sm.OLS(y, sm.add_constant(X[list(comb)]))
        result = model.fit()
        results.append({"model": model, "result": result, "num_vars": len(comb), "vars": X[list(comb)]})

    full_mse_res = sm.OLS(y, sm.add_constant(X)).fit().mse_resid
    acceptable_models = {}

    # Find models which are in line with our conditions
    for model in results:
        not_acceptable = False

        # If a variable has p-value higher than our significance level, reject
        if not all(pvalue < 0.05 for pvalue in model["result"].pvalues):
            continue

        # Set mallows objective to be number of variables in the model
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

    # Mallows plot of best models
    plot_mallows(acceptable_models)

    for var in curr_best["vars"]:
        coef = curr_best["result"].params[var]
        pos_neg = "pos"
        if coef < 0:
            pos_neg = "neg"
        try:
            dct[var + "_" + pos_neg] += 1
        except Exception:
            dct[var + "_" + pos_neg] = 1

def processSubset(X, y, feature_set):
    # Fit model on feature_set and calculate RSS
    model = sm.OLS(y,X[list(feature_set)])
    regr = model.fit()
    RSS = ((regr.predict(X[list(feature_set)]) - y) ** 2).sum()
    return {"model":regr, "RSS":RSS}

def getBest(X, y):
    tic = time.time()
    results = []
    for combo in itertools.combinations(X.columns, 2):
        results.append(processSubset(X, y, combo))
    # Wrap everything up in a nice dataframe
    models = pd.DataFrame(results)
    # Choose the model with the highest RSS
    best_model = models.loc[models['RSS'].argmin()]
    toc = time.time()
    print("Processed ", models.shape[0], "models on", k, "predictors in", (toc-tic), "seconds.")
    # Return the best model, along with some other useful information about the model
    return best_model

def stepwise_selection(X, y,
                       initial_list=[],
                       threshold_in=0.01,
                       threshold_out = 0.05,
                       verbose=True):
    """ Perform a forward-backward feature selection
    based on p-value from statsmodels.api.OLS
    Arguments:
        X - pandas.DataFrame with candidate features
        y - list-like with the target
        initial_list - list of features to start with (column names of X)
        threshold_in - include a feature if its p-value < threshold_in
        threshold_out - exclude a feature if its p-value > threshold_out
        verbose - whether to print the sequence of inclusions and exclusions
    Returns: list of selected features
    Always set threshold_in < threshold_out to avoid infinite looping.
    See https://en.wikipedia.org/wiki/Stepwise_regression for the details
    """
    included = list(initial_list)
    while True:
        changed=False
        # forward step
        excluded = list(set(X.columns)-set(included))
        new_pval = pd.Series(index=excluded)
        for new_column in excluded:
            model = sm.OLS(y, sm.add_constant(pd.DataFrame(X[included+[new_column]]))).fit()
            new_pval[new_column] = model.pvalues[new_column]
        best_pval = new_pval.min()
        if best_pval < threshold_in:
            best_feature = new_pval.argmin()
            included.append(best_feature)
            changed=True
            if verbose:
                print('Add  {:30} with p-value {:.6}'.format(best_feature, best_pval))

        # backward step
        model = sm.OLS(y, sm.add_constant(pd.DataFrame(X[included]))).fit()
        # use all coefs except intercept
        pvalues = model.pvalues.iloc[1:]
        worst_pval = pvalues.max() # null if pvalues is empty
        if worst_pval > threshold_out:
            changed=True
            worst_feature = pvalues.argmax()
            included.remove(worst_feature)
            if verbose:
                print('Drop {:30} with p-value {:.6}'.format(worst_feature, worst_pval))
        if not changed:
            break
    return included

if __name__ == '__main__':
    if len(sys.argv[1:]) == 0:
        raise Exception("No arguments passed - aborting...")
    
    regression_dicts = importlib.import_module("analysis.regression.regression_dicts." + sys.argv[1])
    print (regression_dicts.default_init_steps)
    #Initialize class
    reg_wrap = RegressionWrapper(sys.argv[1])

    #Run dict steps
    reg_wrap.run_dicts(regression_dicts.default_init_steps,
                       regression_dicts.service_steps)

    print (dct)



