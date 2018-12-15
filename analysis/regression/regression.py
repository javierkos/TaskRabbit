import matplotlib
import importlib
import sys
matplotlib.use
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import statsmodels.api as sm
#from analysis.regression.regression_dictsservice_regression_dicts import default_init_steps, service_steps
from analysis.regression.data_prep import DataPreparation
from sklearn.feature_selection import SelectKBest, f_regression
import numpy as np
'''
    Takes one parameter which is the name (key) of the city - eg: new_york, san_francisco etc.
'''

class RegressionWrapper:

    def __init__(self, city_name):
        self.city_name = city_name
        self.data_prep = DataPreparation()

    def run_dicts(self, set_up_dict, regression_dict):
        r2 = {}
        adjusted_r2 = {}
        for service in regression_dict.keys():
            print (service)
            for step in set_up_dict.keys():
                if step == "load":
                    X_data = self.data_prep.data_load(self.city_name, service)
                    X_data = X_data.drop("Av. desc. sentiment", 1)
                elif step == 'store_map':
                    self.data_prep.plot_heatmap(X_data, service)
                elif step == 'init':
                    print("\nSplitting target from input variables...")
                    X, y = self.data_prep.split_target(X_data)
                    print (np.ptp(y.reshape(26,),axis=0))
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
                    print ("SUUUU")
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
                    for i,col in enumerate(cols[1:]):
                        fig, ax = plt.subplots()
                        fig = sm.graphics.plot_fit(est2, i + 1, ax=ax)
                        ax.set_ylabel("Median price")
                        ax.set_xlabel(col)
                        ax.set_title("Linear Regression")
                        plt.show()

        print (r2)
        print (adjusted_r2)

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

    #Initialize class
    reg_wrap = RegressionWrapper(sys.argv[1])

    #Run dict steps
    reg_wrap.run_dicts(regression_dicts.default_init_steps,
                       regression_dicts.service_steps)



