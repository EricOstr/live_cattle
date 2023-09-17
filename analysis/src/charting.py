import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from .data_wrangling import cubicspline
import statsmodels.api as sm

sns.set_style('darkgrid')
plt.rcParams['figure.figsize'] = (16, 8)



def lineplot_2_own_axis(series1, series2, label1="", label2="", title=""):

    fig, ax1 = plt.subplots()

    ax1.plot(series1.index, series1, label=label1, color='blue', alpha=0.5)
    ax1.set_ylabel(label1, color='blue')

    ax2 = ax1.twinx()

    ax2.plot(series2.index, series2, label=label2, color='red', alpha=0.5)
    ax2.set_ylabel(label2, color='red')

    ax1.set_title(title)

    plt.show()





def scatterplot(*args, resample='Y', method='last', label_point=False, reg=False, title='', constant=True):
    '''
    First argument is y, second is x
    '''
    series = []
    labels = []

    for arg in args:
        
        if isinstance(arg, pd.Series):
            series.append(arg)
        elif isinstance(arg, str):
            labels.append(arg)    

    df = pd.concat(
        [
            getattr(series[0].resample(resample), method)(),
            getattr(series[1].resample(resample), method)()
        ], axis=1).dropna()

    df.columns = [0, 1]
    df = df.dropna()

    ax = sns.scatterplot( y=df.iloc[:,0], x=df.iloc[:,1], alpha=0.5, hue=df.index, legend=False)

    if label_point:
        for i, label in enumerate(df.index):
            ax.text(df.iloc[i,0], df.iloc[i,1], label.date(), ha='center', va='center')

    if reg:

        if constant:
            model = sm.OLS(df.iloc[:,0], sm.add_constant(df.iloc[:,1])).fit()
            fitted_values = model.predict(sm.add_constant(df.iloc[:,1]))
        else:
            model = sm.OLS(df.iloc[:,0], df.iloc[:,1]).fit()
            fitted_values = model.predict(df.iloc[:,1])

        
        plt.plot(df.iloc[:,1], fitted_values, color='red')

        plt.text(
            0.05,
            0.85,
            f"{'Intercept estimate: ' + str(round(model.params['const'], 3)) if constant else ''}" + \
            f"'\nSlope estimate: {round(model.params[1], 3)}\n" + \
            f"P-value: {round(model.pvalues[1], 3)}\n" + \
            f"R2-value: {round(model.rsquared, 3)}\n",
            transform=ax.transAxes
        )
        plt.legend()

    if len(labels) == 2:
        plt.ylabel(labels[0])
        plt.xlabel(labels[1])
        

    plt.title(title)
    plt.show()


def lineplot_mult_same_axis(*args, title=""):

    series = []
    labels = []

    for arg in args:
        if isinstance(arg, pd.Series):
            series.append(arg)
        elif isinstance(arg, str):
            labels.append(arg)

    for i, series in enumerate(series):
        label = labels[i] if i < len(labels) else f'series{i}'
        sns.lineplot(data=series, label=label, alpha=0.5)

    plt.title(title)
    plt.legend()
    plt.show()



def lineplot_mult_normalized(*args, legend=True, title=""):

    series = []
    labels = []

    for arg in args:
        if isinstance(arg, pd.Series):
            arg = arg / arg.iloc[0]
            series.append(arg)
        elif isinstance(arg, str):
            labels.append(arg)

    for i, series in enumerate(series):
        label = labels[i] if i < len(labels) else f'series{i}'
        sns.lineplot(data=series, label=label, alpha=0.5, legend=legend)

    plt.title(title)
    plt.show()



def barplot(series, ylim=1, title="", ax=None):
    
    ax = sns.barplot(x=pd.to_datetime(series.index).date, y=series, color='#4c72b0', ax=ax)
    plt.xticks(rotation=45)

    ax.set_ylim(
        min(series) - ylim * abs(min(series)*0.8),
        max(series) + ylim * abs(max(series)*0.2)
        )
    
    plt.title(title)

    return ax


def seasonal_annual_normalized(series, cubic_spline=True, legend=False, title=""):

    groups = series.groupby(series.index.year)

    series = []
    labels = []
    for year, group in groups:

        start_of_year = pd.Timestamp(year=year, month=1, day=1)
        if cubic_spline:
            group = cubicspline(group)
        group.index = (group.index - start_of_year).days
        group.index.name  = 'Day of year'
        
        series.append(group)
        labels.append(year)

    lineplot_mult_normalized(*series, *labels, legend=legend, title=title)


def linear_regression_by_lag(y, x, max_lag=5):

    df = pd.DataFrame()

    df['y'] = y

    for lag in range(0, max_lag+1):
        df[f'x_lag_{lag}'] = x.shift(-lag)

    df = df.dropna()

    for lag in range(max_lag+1):
        X = df.loc[:, f'x_lag_{lag}']
        X = sm.add_constant(X)  # Add a constant (intercept) to the model
        model = sm.OLS(df['y'], X).fit()  # Fit the OLS model
        print(f"Lag {lag}:\t\tSlope = {model.params[1]:.4f}\t\tP-value = {model.pvalues[1]:.4f}")



def plot_fitted_actual(actual, fitted):
        
    import plotly.graph_objs as go
    from plotly.subplots import make_subplots
    import numpy as np

    # create a subplot with two traces
    fig = make_subplots(rows=1, cols=1)

    fig.add_trace(go.Scatter(x=fitted.index, y=actual[fitted.index], mode='markers', name='Actual', marker=dict(color='blue')),
                row=1, col=1)

    fig.add_trace(go.Scatter(x=fitted.index, y=fitted, mode='markers', name='Fitted', marker=dict(color='red')),
                row=1, col=1)

    # add lines connecting predicted to actual values
    for i in range(len(fitted)):
        fig.add_shape(type='line',
                    x0=fitted.index[i], y0=fitted[i],
                    x1=fitted.index[i], y1=actual[fitted.index[i]],
                    line=dict(color='red', width=1))

    # update layout
    fig.update_layout(title='Fitted vs. Actual Values',
                    xaxis_title='Date',
                    yaxis_title='Cattle cash price % change')


    print('Mean Absolute Error:', round(np.mean(abs(actual[fitted.index] - fitted)), 2))
    # show plot
    fig.show()



def plot_coefficients_pvalues(model):


    # extract parameter estimates and p-values from the summary table
    params = model.params
    pvalues = model.pvalues

    # plot the parameter estimates
    fig, (ax1, ax2) = plt.subplots(nrows=2, gridspec_kw={'height_ratios': [2, 1]})
    params.plot(kind='bar', ax=ax1)
    ax1.set_ylabel('Parameter Estimate')
    ax1.set_xticklabels([])  # remove x ticks

    # plot the p-values
    pvalues.plot(kind='bar', ax=ax2, color='grey')
    ax2.axhline(y=0.1, color='red', linestyle='--')
    ax2.set_ylabel('p-value')
    ax2.set_xlabel('Parameter')
    plt.show()    



def plot_monthly_box_chart_plotly(series, title="", ylabel="", xlabel=""):

    df_adj = pd.DataFrame({
        'series': series,
        'month' : series.index.month,
    })

    import plotly.subplots as sp

    fig = sp.make_subplots(rows=1, cols=1)

    fig.add_box(y=df_adj['series'], x=df_adj['month'], name='Price Received')

    fig.update_layout(title=title,
                    xaxis_title=xlabel,
                    yaxis_title=ylabel)

    fig.show()

    import matplotlib.pyplot as plt


def plot_monthly_box_chart_matplotlib(series, title="", ylabel="", xlabel=""):
    
    df_adj = pd.DataFrame({
        'series': series,
        'month': series.index.month,
    })

    plt.figure(figsize=(10, 6))  # Adjust the figure size as needed

    # Create a list of labels for each month
    month_labels = df_adj['month'].unique()
    month_labels.sort()

    # Create a list to store data for each month
    data_by_month = [df_adj[df_adj['month'] == month]['series'] for month in month_labels]

    # Create a box plot for the series by month
    plt.boxplot(data_by_month, labels=month_labels)

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    plt.grid(True)
    plt.tight_layout()
    plt.show()