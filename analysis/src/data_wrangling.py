import pandas as pd
import datetime
import requests
from bs4 import BeautifulSoup


class Config:
    analysis_start_date = pd.to_datetime(datetime.date(2000,1,1)) # 200-01-01 was a Saturday, first trading day on 3rd


month_to_number = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
}

number_to_month = {
    0: 'Jan', 1: 'Feb', 2: 'Mar', 3: 'Apr', 4: 'May', 5: 'Jun',
    6: 'Jul', 7: 'Aug', 8: 'Sep', 9: 'Oct', 10: 'Nov', 11: 'Dec'
}


def cubicspline(series, freq='D'):
    '''
    Takes in a series and returns a series with <freq> values interpolated using cubic splines
    '''

    series = series.asfreq(freq)
    series = series.interpolate(method='cubicspline')
    
    return series


def clean_tv_data(df, historical=False):
    '''
    Cleans data coming from Trading View. Returns the closing price
    '''
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df = df.rename(columns={'time': 'Date'})
    df = df.set_index('Date')
    df.index = pd.to_datetime(df.index.date)

    if not historical:
        df = df[df.index >= Config.analysis_start_date]

    return df.close


def combine_to_datetime(row):
    period_to_month = {
        'FIRST OF JAN': '01',
        'FIRST OF JUL': '07'
    }
    month = period_to_month.get(row['Period'], '01')

    return pd.to_datetime(f"{row['Year']}-{month}", format="%Y-%m")


def usda_clean_annual(df, end_of_year=True, historical=False):

    if type(df.Value[0]) == str:
        df['Value'] = df['Value'].str.replace(',', '').astype(float) 
    else:
        df['Value'] = df['Value'].astype(float)

    df['Date'] = pd.to_datetime(df.Year, format='%Y', errors='coerce') + (pd.offsets.YearEnd(0) if end_of_year else pd.offsets.YearBegin(0))
    df.drop(['Year'], axis=1, inplace=True) 

    df = df.set_index('Date')
    df = df.sort_index(ascending=True)
    df.index = pd.to_datetime(df.index.date)

    if not historical:
        df = df[df.index >= Config.analysis_start_date]

    return df.Value


def usda_clean_biannual(df, historical=False):

    if type(df.Value[0]) == str:
        df['Value'] = df['Value'].str.replace(',', '').astype(float) 
    else:
        df['Value'] = df['Value'].astype(float)    

    df['Date'] = df.apply(combine_to_datetime, axis=1)
    df.drop(['Year', 'Period'], axis=1, inplace=True)

    df = df.set_index('Date')
    df = df.sort_index(ascending=True)
    df.index = pd.to_datetime(df.index.date)        
    
    if not historical:
        df = df[df.index >= Config.analysis_start_date]

    return df.Value


# def adjust_value_by_inflation(df, val_col='Value', inflation_rate=0.02):

#     df = df.sort_index()
#     reference_row = df.iloc[0]

#     for i, other_row in df.iterrows():
#         if i == df.index[0]:
#             continue
#         else:
#             days_diff = (other_row.name - reference_row.name).days
#             inflation_factor = (1 + inflation_rate/365) ** days_diff
#             df.at[i, val_col] = other_row[val_col] / inflation_factor
    
#     df = df[df.index >= Config.analysis_start_date]    

#     return df


def adjust_series_cpi(series):

    cpi_series = cubicspline(get_cpi_series(historical=True))
    
    cpi_series = cpi_series[cpi_series.index >= series.index[0]]
    series = series[series.index >= cpi_series.index[0]]

    cpi_series_rebased = cpi_series / cpi_series[0]

    return (series / cpi_series_rebased).dropna()



def get_inflation_historical_series():

    response = requests.get('https://www.usinflationcalculator.com/inflation/historical-inflation-rates/')
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find('table')
    df = pd.read_html(str(table))[0]

    df = df.drop(['Ave'], axis=1)


    df_melted = df.melt(id_vars=["Year"], var_name="Month", value_name="Inflation")

    df_melted["Month"] = df_melted["Month"].map(month_to_number)

    # Convert the "Year" and "Month" columns to datetime format and set it as the index
    df_melted["Date"] = pd.to_datetime(df_melted["Year"].astype(str) + "-" + df_melted["Month"].astype(str) + "-1")
    df_melted.set_index("Date", inplace=True)

    # Drop unnecessary columns and sort
    df_melted.drop(columns=["Year", "Month"], inplace=True)
    df_melted.sort_index(inplace=True)
    historical_inflation.index = historical_inflation.index.date

    historical_inflation = pd.to_numeric(df_melted.Inflation, errors='coerce').dropna()

    return historical_inflation


def get_cpi_series(historical=False):
    '''
    Monthly CPI for All Urban Consumers (CPI-U)
    source: https://www.usinflationcalculator.com/inflation/consumer-price-index-and-annual-percent-changes-from-1913-to-2008/
    '''

    url = 'https://www.usinflationcalculator.com/inflation/consumer-price-index-and-annual-percent-changes-from-1913-to-2008/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find('table')
    df = pd.read_html(str(table), header=0, skiprows=[0])[0]

    df = df.drop(['Avg', 'Dec-Dec', 'Avg-Avg', 'Unnamed: 16'], axis=1)
    
    df_melted = df.melt(id_vars=["Year"], var_name="Month", value_name="CPI")

    # Replace month names with corresponding month numbers
    month_to_number = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'June': 6,
        'July': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }
    df_melted["Month"] = df_melted["Month"].map(month_to_number)


    # Convert the "Year" and "Month" columns to datetime format and set it as the index
    df_melted["Date"] = pd.to_datetime(df_melted["Year"].astype(str) + "-" + df_melted["Month"].astype(str) + "-1")
    df_melted.set_index("Date", inplace=True)
    df_melted.index = df_melted.index.date
    df.index = pd.to_datetime(df.index)


    # Drop unnecessary columns and sort
    df_melted.drop(columns=["Year", "Month"], inplace=True)
    df_melted.sort_index(inplace=True)

    cpi_series = pd.to_numeric(df_melted.CPI, errors='coerce').dropna()

    if not historical:
        cpi_series = cpi_series[cpi_series.index >= Config.analysis_start_date]

    return cpi_series


def get_us_gdp_qrt_historical_series():
    '''
    Quarterly US Nominal GDP
    source: https://www.multpl.com/us-gdp/table/by-quarter 
    '''
    url = 'https://www.multpl.com/us-gdp/table/by-quarter'

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find('table')
    df = pd.read_html(str(table))[0]

    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df.sort_index(inplace=True)
    df.index = pd.to_datetime(df.index.date)

    # Convert the string numbers to actual numeric type
    df['GDP'] = pd.to_numeric(df['Value Value'].str.replace(' trillion', '')) * (10**12)
    df.drop(['Value Value'], axis=1, inplace=True)

    return df.GDP




def get_sp500_historical_series():

    '''
    Monthly SP500
    https://www.multpl.com/s-p-500-historical-prices/table/by-month
    '''
    url = 'https://www.multpl.com/s-p-500-historical-prices/table/by-month'

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find('table')
    df = pd.read_html(str(table))[0]

    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df.sort_index(inplace=True)
    df.index = pd.to_datetime(df.index.date)

    df['SP500'] = df['Price Value']
    df.drop(['Price Value'], axis=1, inplace=True)

    return df.SP500




def get_us_gdp_qrt_historical_series():
    '''
    Quarterly US Nominal GDP
    source: https://www.multpl.com/us-gdp/table/by-quarter 
    '''
    url = 'https://www.multpl.com/us-gdp/table/by-quarter'

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find('table')
    df = pd.read_html(str(table))[0]

    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df.sort_index(inplace=True)
    df.index = pd.to_datetime(df.index.date)

    # Convert the string numbers to actual numeric type
    df['GDP'] = pd.to_numeric(df['Value Value'].str.replace(' trillion', '')) * (10**12)
    df.drop(['Value Value'], axis=1, inplace=True)

    return df.GDP


def get_sp500_historical_series():

    '''
    Monthly SP500
    https://www.multpl.com/s-p-500-historical-prices/table/by-month
    '''
    url = 'https://www.multpl.com/s-p-500-historical-prices/table/by-month'

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find('table')
    df = pd.read_html(str(table))[0]

    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df.sort_index(inplace=True)
    df.index = pd.to_datetime(df.index.date)

    df['SP500'] = df['Price Value']
    df.drop(['Price Value'], axis=1, inplace=True)

    return df.SP500





def get_us_gdp_qrt_series():

    gdp_historical = get_us_gdp_qrt_historical_series()
    gdp = gdp_historical[gdp_historical.index >= Config.analysis_start_date]

    return gdp


def combine_month_to_datetime(row):
    period_to_month = {
        'JAN': '01',
        'FEB': '02',
        'MAR': '03',
        'APR': '04',
        'MAY': '05',
        'JUN': '06',
        'JUL': '07',
        'AUG': '08',
        'SEP': '09',
        'OCT': '10',
        'NOV': '11',
        'DEC': '12'
    }
    month = period_to_month.get(row['Period'], '01')

    return pd.to_datetime(f"{row['Year']}-{month}-01", format="%Y-%m-%d")



def usda_clean_monthly(df, only_value=True, historical=False):


    if type(df.Value[0]) == str:
        df['Value'] = df['Value'].str.replace(',', '').astype(float) 
    else:
        df['Value'] = df['Value'].astype(float)


    df['Date'] = df.apply(combine_month_to_datetime, axis=1)
    df.drop(['Year', 'Period', 'Week Ending'], axis=1, inplace=True)

    df = df.set_index('Date')
    df = df.sort_index(ascending=True)

    if not historical:
        df = df[df.index >= Config.analysis_start_date]        

    return df.Value if only_value else df




def get_us_population_historical_series():
    '''
    US 
    '''
    url = 'https://www.multpl.com/united-states-population/table/by-month'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find('table')
    df = pd.read_html(str(table))[0]


    df['Date'] = pd.to_datetime(df['Date'], format='%b %d, %Y')

    df.set_index('Date', inplace=True)
    df.sort_index(inplace=True)
    # df.index = df.index.date


    df['Value'] = df['Value Value'].str.replace('[^\d.]', '', regex=True).astype(float)*1e6

    return df['Value']


def clean_fas_data(data):

    data = data.drop(columns=['UOM'])
    data = data.melt(id_vars=['Year'], var_name='Month', value_name='Value')

    def get_date(row):
        year = row.Year.split('-')[0]
        month_number = pd.to_datetime(row.Month, format="%B").month
        return pd.to_datetime(f"{year}-{month_number}-1")

    def get_pounds(row):
        # Convert from metric tons string value to pounds (lb) float value
        return float(row.Value.replace(',', ''))

    data['Date'] = data.apply(get_date, axis=1)

    data = data[['Date','Value']]
    data = data.dropna()
    data.set_index('Date', inplace=True)
    data.sort_index(inplace=True)
    # data.index = data.index.date

    data.Value = data.apply(get_pounds, axis=1)

    return data.Value



def pop_row(dataframe, index_to_split):
    # Get the row to split
    row_to_split = dataframe.iloc[index_to_split:index_to_split + 1]

    # Create a DataFrame without the specified row
    dataframe_without_row = dataframe.drop(row_to_split.index)

    return row_to_split, dataframe_without_row



