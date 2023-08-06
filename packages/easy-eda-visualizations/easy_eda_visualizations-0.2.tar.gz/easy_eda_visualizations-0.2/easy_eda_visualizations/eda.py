import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns


class EDA():
    def __init__(self, df):
        '''
        Class that can be used to plot charts like histograms, boxplots, kdeplots etc. to perform EDA
        Attributes: df, defines the dataframe that should be inspected
        '''
        self.df = df

    def nans(self, threshold=None):
        '''
        :param threshold: define an optional threshold to only display columns that contain more than threshold% nans
        :return: returns a dataframe that displays the number and percentage of nans in each column of the self.df object
        '''
        nan_percentage = round((np.sum(self.df.isnull()) / self.df.shape[0]) * 100, 1)
        nan_sum = np.sum(self.df.isnull())
        df_columns = self.df.columns
        df_nans = pd.DataFrame({'Column': df_columns, '# Nan values': nan_sum, '% Nan values': nan_percentage}).reset_index(drop=True).sort_values(by='% Nan values', ascending=False).reset_index(drop=True)
        if threshold is None:
            return df_nans
        else:
            df_nan_percentage = df_nans[df_nans['% Nan values'] >= threshold].reset_index(drop=True).sort_values(by='% Nan values', ascending=False).reset_index(drop=True)
            return df_nans

    def histograms(self, columns=None, n_columns=3, subplot_width=5, subplot_height=5, sns_theme='whitegrid', bins=20):
        '''
        :param columns (list of strings): pass list of columns to select subset of dataframe
        :param n_columns (int): specify how many columns the output figure should have
        :param subplot_width (int): specify the width of all subplots
        :param subplot_height (int): specify the height of all subplots
        :param sns_theme (string): specify the sns theme for the subplots
        :param bins (int): specify how many bins the histogram should have
        :return: plots a figure containing a histogram for each column in the df or each colum specified in columns
        '''

        # Check if a value for columns is passed and select only numeric columns out of df
        if columns is None:
            df = self.df.select_dtypes(include='number')
        else:
            df = self.df[columns].select_dtypes(include='number')

        # Determine number of rows, number of columns and the figure size
        number_plots = len(df.columns)
        n_rows = number_plots
        n_columns = n_columns
        while n_rows % n_columns != 0:
            n_rows += 1
        n_rows = int(n_rows / n_columns)
        figure_width = subplot_width * n_columns
        figure_height = subplot_height * n_rows

        # Create histograms
        plt.clf()
        sns.set_theme(style=sns_theme)
        figure = plt.figure(figsize=(figure_width, figure_height))
        figure.subplots_adjust(hspace=0.3, wspace=0.3)
        for n, col in enumerate(df.columns):
            ax = plt.subplot(n_rows,n_columns,n+1)
            sns.histplot(df[col], bins=bins)
            plt.title(col, fontsize=16)
            ax.set(ylabel=None)
            ax.set(xlabel=None)
            plt.xticks(fontsize=14)
            plt.yticks(fontsize=14)
        plt.show()


    def boxplots(self, columns=None, n_columns=3, subplot_width=5, subplot_height=5, sns_theme='whitegrid'):
        '''
        :param columns (list of strings): pass list of columns to select subset of dataframe
        :param n_columns (int): specify how many columns the output figure should have
        :param subplot_width (int): specify the width of all subplots
        :param subplot_height (int): specify the height of all subplots
        :param sns_theme (string): specify the sns theme for the subplots
        :return: plots a figure containing a boxplot for each column in the df or each colum specified in columns
        '''
        # Check if a value for columns is passed and select only numeric columns out of df
        if columns is None:
            df = self.df.select_dtypes(include='number')
        else:
            df = self.df[columns].select_dtypes(include='number')

        # Determine number of rows, number of columns and the figure size
        number_plots = len(df.columns)
        n_rows = number_plots
        n_columns = n_columns
        while n_rows % n_columns != 0:
            n_rows += 1
        n_rows = int(n_rows / n_columns)
        figure_width = subplot_width * n_columns
        figure_height = subplot_height * n_rows

        # Create boxplots
        plt.clf()
        sns.set_theme(style=sns_theme)
        plt.figure(figsize=(figure_width, figure_height))
        plt.subplots_adjust(hspace=0.3, wspace=0.3)
        for n, col in enumerate(df.columns):
            ax = plt.subplot(n_rows,n_columns,n+1)
            sns.boxplot(data=df[col])
            plt.title(col, fontsize=16)
            ax.set(ylabel=None)
            ax.set(xlabel=None)
            plt.xticks(fontsize=14)
            plt.yticks(fontsize=14)
        plt.show()

    def violinplots(self, columns=None, n_columns=3, subplot_width=5, subplot_height=5, sns_theme='whitegrid'):
        '''
        :param columns (list of strings): pass list of columns to select subset of dataframe
        :param n_columns (int): specify how many columns the output figure should have
        :param subplot_width (int): specify the width of all subplots
        :param subplot_height (int): specify the height of all subplots
        :param sns_theme (string): specify the sns theme for the subplots
        :return: plots a figure containing a violin plot for each column in the df or each colum specified in columns
        '''

        # Check if a value for columns is passed and select only numeric columns out of df
        if columns is None:
            df = self.df.select_dtypes(include='number')
        else:
            df = self.df[columns].select_dtypes(include='number')

        # Determine number of rows, number of columns and the figure size
        number_plots = len(df.columns)
        n_rows = number_plots
        n_columns = n_columns
        while n_rows % n_columns != 0:
            n_rows += 1
        n_rows = int(n_rows / n_columns)
        figure_width = subplot_width * n_columns
        figure_height = subplot_height * n_rows

        # Create violinplots
        plt.clf()
        sns.set_theme(style=sns_theme)
        plt.figure(figsize=(figure_width, figure_height))
        plt.subplots_adjust(hspace=0.3, wspace=0.3)
        for n, col in enumerate(df.columns):
            ax = plt.subplot(n_rows,n_columns,n+1)
            sns.violinplot(x=df[col])
            plt.title(col, fontsize=16)
            ax.set(ylabel=None)
            ax.set(xlabel=None)
            plt.xticks(fontsize=14)
            plt.yticks(fontsize=14)
        plt.show()

    def kdeplots(self, columns=None, n_columns=3, subplot_width=5, subplot_height=5, sns_theme='whitegrid'):
        '''
        :param columns (list of strings): pass list of columns to select subset of dataframe
        :param n_columns (int): specify how many columns the output figure should have
        :param subplot_width (int): specify the width of all subplots
        :param subplot_height (int): specify the height of all subplots
        :param sns_theme (string): specify the sns theme for the subplots
        :return: plots a figure containing a kde plot for each column in the df or each colum specified in columns
        '''

        # Check if a value for columns is passed and select only numeric columns out of df
        if columns is None:
            df = self.df.select_dtypes(include='number')
        else:
            df = self.df[columns].select_dtypes(include='number')

        # Determine number of rows, number of columns and the figure size
        number_plots = len(df.columns)
        n_rows = number_plots
        n_columns = n_columns
        while n_rows % n_columns != 0:
            n_rows += 1
        n_rows = int(n_rows / n_columns)
        figure_width = subplot_width * n_columns
        figure_height = subplot_height * n_rows

        # Create kdeplots
        plt.clf()
        sns.set_theme(style=sns_theme)
        plt.figure(figsize=(figure_width, figure_height))
        plt.subplots_adjust(hspace=0.3, wspace=0.3)
        for n, col in enumerate(df.columns):
            ax = plt.subplot(n_rows,n_columns,n+1)
            sns.kdeplot(df[col], shade=True, alpha=0.7)
            plt.title(col, fontsize=16)
            ax.set(ylabel=None)
            ax.set(xlabel=None)
            plt.xticks(fontsize=14)
            plt.yticks(fontsize=14)
        plt.show()

    def correlation_heatmap(self, columns=None, sns_theme='whitegrid', correlation_method='pearson', target=None):
        '''
        :param columns (list of strings): pass list of columns to select subset of dataframe
        :param sns_theme (string): specify the sns theme for the subplots
        :param correlation_method (string): specify which correlation method should be used to calculate correlations (e.g. pearson, spearman)
        :param target (string): specify if the heatmap should be only created for a target column
        :return: plots a heatmap which displays the correlations for each column in the dataframe or each column in columns
        '''
        # Check if a value for columns is passed and select only numeric columns out of df
        if columns is None:
            df = self.df.select_dtypes(include='number')
        elif columns is not None:
            df = self.df[columns].select_dtypes(include='number')

        # Create correlation df
        correlation_df = df.corr(method=correlation_method)

        # Check if a value for target is passed
        if target is None:

            # Determine figure size
            figure_height = len(correlation_df)
            figure_width = len(correlation_df)

            # Create correlation heatmap
            plt.clf()
            sns.set_theme(style=sns_theme)
            plt.figure(figsize=(figure_width,figure_height))
            sns.heatmap(correlation_df, annot=True, fmt='.2f')
            plt.title('Correlation heatmap', fontsize=18)
            plt.show()

        elif target is not None:

            # Create sorted df containing only correlations for the target
            correlation_df = correlation_df[[target]].sort_values(by=target, ascending=False).copy()

            # Determine figure height (figure_width not needed)
            figure_height = len(correlation_df)

            # Create correlation heatmap
            plt.clf()
            sns.set_theme(style=sns_theme)
            plt.figure(figsize=(10,figure_height))
            sns.heatmap(correlation_df, annot=True, fmt='.2f')
            plt.title('Correlation heatmap for: {target}'.format(target=target), fontsize=16)
            plt.show()

    def scatterplot(self, columns, sns_theme='whitegrid'):
        '''
        :param columns (list of strings): pass list of columns to select subset of dataframe
        :param sns_theme (string): specify the sns theme for the subplots
        :return: plots a scatterplot of the two columns specified in columns
        '''
        # Create df with relevant columns
        df = self.df[columns]

        # Save columns as series for scatterplot
        column_one = df.iloc[:, 0]
        column_two = df.iloc[:, 1]

        # Create scatterplot
        plt.clf()
        sns.set_theme(style=sns_theme)
        plt.figure(figsize=(10,10))
        sns.scatterplot(x=column_one, y=column_two)
        plt.title('{column_one} vs. {column_two}'.format(column_one=columns[0], column_two=columns[1]), fontsize=16)
        plt.xticks(fontsize=16)
        plt.yticks(fontsize=16)
        plt.xlabel(xlabel=columns[0], fontsize=14)
        plt.ylabel(ylabel=columns[1], fontsize=14)
        plt.show()