import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from .data_wrangling import cubicspline

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



def scatterplot(*args, resample='M', method='last', label_point=False, reg=False):

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

    ax = sns.scatterplot(x=df.iloc[:,0], y=df.iloc[:,1], alpha=0.5, hue=df.index, legend=False)

    if label_point:
        for i, label in enumerate(df.index):
            ax.text(df.iloc[i,0], df.iloc[i,1], label.date(), ha='center', va='center')

    if reg:
        # Add regression line with slope and intercept
        slope, intercept, r_value, p_value, std_err = stats.linregress(df.iloc[:,0], df.iloc[:,1])
        r2_value = r_value ** 2
        sns.regplot(x=df.iloc[:,0], y=df.iloc[:,1], scatter=False, color='red', ci=None, line_kws={'label':"y={0:.3f}x+{1:.3f}".format(slope,intercept)})
        plt.text(0.05, 0.95, "Slope estimate: {0:.3f}\nIntercept estimate: {1:.3f}\nP-value: {2:.3f}\nR2-value: {3:.3f}".format(slope, intercept, p_value, r2_value), transform=ax.transAxes, fontsize=12, verticalalignment='top')
        plt.legend()

    if len(labels) == 2:
        plt.xlabel(labels[0])
        plt.ylabel(labels[1])

    plt.show()


def lineplot_mult_same_axis(*args, **kwargs):

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


def linear_regression_by_lag(dep_var_series, indep_var_series, max_lag=5):

    df = pd.DataFrame()

    df['dep_var'] = dep_var_series

    for lag in range(0, max_lag+1):
        df[f'indep_var_lag_{lag}'] = indep_var_series.shift(-lag)

    df = df.dropna()


    for lag in range(max_lag+1):

        slope, intercept, r_value, p_value, std_err = stats.linregress(
            df.loc[:,'dep_var'],
            df.loc[:,f'indep_var_lag_{lag}']
        )

        print(f"Lag {lag}:\t\tSlope = {slope:.4f}\t\tP-value = {p_value:.4f}")

