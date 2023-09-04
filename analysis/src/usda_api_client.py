import urllib.request
import pandas as pd
import urllib.parse
from requests.utils import requote_uri
from dotenv import load_dotenv
import os
import io


class usda_quick_stats_dataframe:

    def __init__(self):

        load_dotenv()

        self.base_url_api_get = 'http://quickstats.nass.usda.gov/api/api_GET/?key=' + \
            os.environ['USDA_API_KEY'] + '&'
        self.output_file_path = r'csv_raw/'



    def query(self):
        pass

    def get_data_df(self, parameters):

        s_result = urllib.request.urlopen(self.base_url_api_get + parameters)
        s_text = s_result.read().decode('utf-8')

        df = pd.read_csv(io.StringIO(s_text))

        return df

    def get_data_csv(self, parameters, file_name):

        s_result = urllib.request.urlopen(self.base_url_api_get + parameters)
        s_text = s_result.read().decode('utf-8')

        s_file_name = self.output_file_path + file_name + ".csv"
        o_file = open(s_file_name, "w", encoding="utf8")
        o_file.write(s_text)

        o_file()


    def create_query_string(self,
                            source_desc=None,
                            sector_desc=None,
                            commodity_desc=None,
                            statisticcat_desc=None,
                            unit_desc=None,
                            freq_desc=None,
                            reference_period_desc=None,
                            year__GE=None,
                            agg_level_desc=None,
                            state_name=None,
                            format=None,
                            ):

        return 'source_desc=SURVEY' +  \
            '&' + urllib.parse.quote('sector_desc=FARMS & LANDS & ASSETS') + \
            '&' + urllib.parse.quote('commodity_desc=FARM OPERATIONS') + \
            '&' + urllib.parse.quote('statisticcat_desc=AREA OPERATED') + \
            '&unit_desc=ACRES' + \
            '&freq_desc=ANNUAL' + \
            '&reference_period_desc=YEAR' + \
            '&year__GE=1997' + \
            '&agg_level_desc=NATIONAL' + \
            '&' + urllib.parse.quote('state_name=US TOTAL') + \
            '&format=CSV'
