import numpy as np
import os
import matplotlib
matplotlib.use
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from sklearn import preprocessing
from scipy import stats
import operator
from statsmodels.stats.outliers_influence import variance_inflation_factor
import pickle

class DataPreparation:

    def plot_heatmap(self, df, service_name, type='kendall', save=True):
        '''
        fig1, ax1 = plt.subplots()
        fig1.set_size_inches(16, 12)
        plt.title("Correlation between variables for New York boroughs on " + service_name + " service")
        plt.gcf().subplots_adjust(bottom=0.35, left=0.35)
        sns.heatmap(df.corr(type),
                    xticklabels=df.corr(type).columns.values,
                    yticklabels=df.corr(type).columns.values)
        plt.savefig("../plots/heat_maps/" + service_name + ".png") if save else plt.show()
        '''

    def plot_histogram(self, column, column_name, save=True):
        fig1, ax1 = plt.subplots()
        plt.title("Histogram of " + column_name + "")

        plt.hist(column)

        plt.savefig("../plots/histograms/" + column_name + ".png") if save else plt.show()

    def distribution_tests(self, column):
        kstest_results = {}

        #Different fit functions for different distributions we want to test
        distribution_funcs = {
            "norm": stats.norm.fit,
            "lognorm": stats.lognorm.fit,
            "expon": stats.expon.fit,
            "exponnorm": stats.exponnorm.fit,
            "gamma": stats.exponnorm.fit,
            "t": stats.t.fit, #Students T
            "beta": stats.beta.fit
        }

        #For each distribution we want to test
        for dist in distribution_funcs.keys():
            #Fit the variable to the distribution
            fit = distribution_funcs[dist](column)
            #Then perform ks test and get the test statistic
            kstest_results[dist] = stats.kstest(column, dist, fit)[0]
        return sorted(kstest_results.items(), key=operator.itemgetter(1))
        return kstest_results

    def scale_data(self, df):
        standardised = preprocessing.scale(df)
        return pd.DataFrame(standardised, index=df.index, columns=df.columns)

    def normal_test(self, column):
        return {
            "skew": stats.skew(column),
            "kurtosis": stats.kurtosis(column)
        }
    def shapiro_test(self, column):
        return stats.shapiro(column)

    #This function was stolen from: https://stats.stackexchange.com/questions/155028/how-to-systematically-remove-collinear-variables-in-python
    def calculate_vif_(self, X, thresh=5.0):
        variables = list(range(X.shape[1]))
        dropped = True
        while dropped:
            dropped = False
            vif = [variance_inflation_factor(X.iloc[:, variables].values, ix)
                   for ix in range(X.iloc[:, variables].shape[1])]

            maxloc = vif.index(max(vif))
            if max(vif) > thresh:
                print('dropping \'' + X.iloc[:, variables].columns[maxloc] +
                      '\' at index: ' + str(maxloc))
                del variables[maxloc]
                dropped = True

        print('Remaining variables:')
        print(X.columns[variables])
        return X.iloc[:, variables]

    def split_target(self, X_data):
        # Get target values into y, remove from X
        y = np.array(X_data['Median service cost']).reshape(X_data['Median service cost'].shape[0], 1)

        # data_prep.plot_heatmap(X_data, "Delivery cost")
        X = X_data.drop('Median service cost', 1)
        return X, y

    def data_load(self, location, service, relative=False):
        # Read dataframe for service
        if relative:
            with open("dataframes/" + location + "/" + service + ".pkl", 'rb') as f:
                return pickle.load(f)
        else:
            with open("../dataframes/" + location + "/" + service + ".pkl", 'rb') as f:
                return pickle.load(f)