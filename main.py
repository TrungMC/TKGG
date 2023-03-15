# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os.path

import pandas as pd
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime


class EasyStock():
    @staticmethod
    def read_gsheet_data():
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        SAMPLE_RANGE_NAME = 'Class Data!A2:E'
        EASY_STOCK_SHEET_ID = '1AQYyd5KP913Qrgy3ZVQSbjYiNQOK-XsulfGn39nRM-o'
        PS_RANGE_NAME = 'Thong Ke!A2:H'
        # connect got Google Sheets
        gc = gspread.service_account(filename="token.json")
        # list all available spreadsheets
        wks = gc.open_by_url(
            'https://docs.google.com/spreadsheets/d/1AQYyd5KP913Qrgy3ZVQSbjYiNQOK-XsulfGn39nRM-o/edit#gid=0').worksheet(
            'Thong ke')
        data = wks.get_all_values()
        return data

    @staticmethod
    def format_date(datestr):
        if len(datestr) <= 5:
            datestr = datestr + "/2023"

        date = datetime.strptime(datestr, '%d/%m/%Y')
        return datetime.strftime(date, '%Y-%m-%d')

    @staticmethod
    def format_ps_date(datestr):
        date = datetime.strptime(datestr, '%d/%m/%Y')
        return datetime.strftime(date, '%Y-%m-%d')

    @staticmethod
    def format_all_buy_sell_date(datestr):
        if len(datestr) <= 5:
            datestr = datestr + "/2023"
        return datetime.strptime(datestr, '%d/%M/%Y').strftime('%d/%M')

    @staticmethod
    def get_last_day(data):
        last_index = data[1][10]
        return f'2023_{last_index[3:]}_{last_index[0:2]}'

    @staticmethod
    def get_transaction_df(data, save=False):
        trans_df = pd.DataFrame(data[:27]).iloc[1:, :11]
        new_df = trans_df.T
        header = new_df.iloc[0]
        header[1] = 'Date'
        new_df.index.name = 'id'
        new2_df = new_df
        new2_df.columns = header
        new2_df = new2_df.iloc[1:, :]
        for col in new2_df.columns:

            if col and col not in ['id', 'Date', 'Vnindex (%)']:
                new2_df[col] = new2_df[col].str.replace(',', '', regex=True).astype(int)
                # new2_df[col] = pd.to_numeric(new2_df[col])
        new2_df['Date'] = [EasyStock.format_date(d) for d in new2_df['Date']]
        if save:
            last_index = new2_df.iloc[-1, 0]
            last_index = f'2023_{last_index[3:]}_{last_index[0:2]}'
            file_name = last_index + "_KLGDCS.csv"
            new2_df.to_csv("data/" + file_name, sep=',')
            new2_df.to_csv("data/" + "KLGDCS.csv", sep=',')
        return new2_df

    def to_numeric(text_number):
            if not text_number:
                return 0

            last_group=text_number.split('.')[-1]
            if not last_group:
                return 0

            print(f"Procesing {text_number} with last group {last_group}")
            if len(last_group)>0 and len(last_group)<3:
                return text_number.split('.',)[0]
            else:
                return text_number.replace('.','')
    @staticmethod
    def get_derevative_df(data, save=False):
        derevative_header = ['Date', 'CN_Long', 'CN_Short', 'TD_Long', 'TD_Short', 'NN_Long', 'NN_Short', 'Total_Long',
                             'Total_Short','Open_Interest']
        derevative_df = pd.DataFrame(data[138:163]).iloc[:, 7:17]
        derevative_df.columns = derevative_header
        derevative_df.index.name = 'id'
        for col in derevative_header[1:]:
            #derevative_df[col] = [lambda x:EasyStock.to_numeric(x) for x in derevative_df[col]]
            derevative_df[col] = derevative_df[col].apply(EasyStock.to_numeric)
            derevative_df[col] = pd.to_numeric(derevative_df[col])

        derevative_df = derevative_df[derevative_df['CN_Long'] > 0]
        derevative_df['CN_Net'] = derevative_df['CN_Long'] - derevative_df['CN_Short']
        derevative_df['TD_Net'] = derevative_df['TD_Long'] - derevative_df['TD_Short']
        derevative_df['NN_Net'] = derevative_df['NN_Long'] - derevative_df['NN_Short']
        derevative_df['Total_Net'] = derevative_df['Total_Long'] - derevative_df['Total_Short']
        derevative_df['Date'] = [EasyStock.format_date(d) for d in derevative_df['Date']]
        file_name = 'KLGDPS.csv'
        if save:
            last_day = EasyStock.get_last_day(data)
            derevative_df.to_csv("data/" + file_name, sep=',')
            derevative_df.to_csv("data/" + last_day + "_KLGDPS.csv", sep=',')
        return derevative_df

    @staticmethod
    def dataframe_to_csv(df, col4="NN"):
        rows = []
        for i in range(0, 9):
            for j in range(1, 11):
                date = df.iloc[i, 1]
                if not date:
                    print(df)
                    raise "Date not found"
                s = df.iloc[i, j]
                if "[" in s:
                    parts = s.split("[")
                    name = parts[0].strip()
                    value = parts[1].replace("]", "").strip()
                    rows += [[date, name, value, col4]]

        return pd.DataFrame(rows, columns=["Date", "Code", "Value", "Source"])

    @staticmethod
    def get_top_buy_sell(data, save=False):
        last_day = EasyStock.get_last_day(data)
        nn_buy = pd.DataFrame(data[30:41]).iloc[:, 1:12].T
        nn_sell = pd.DataFrame(data[41:52]).iloc[:, 1:12].T
        td_buy = pd.DataFrame(data[57:68]).iloc[:, 1:12].T
        td_sell = pd.DataFrame(data[68:79]).iloc[:, 1:12].T

        nn_buy_df = EasyStock.dataframe_to_csv(nn_buy, "NN")
        nn_sell_df = EasyStock.dataframe_to_csv(nn_sell, "NN")
        td_buy_df = EasyStock.dataframe_to_csv(td_buy, "TD")
        td_sell_df = EasyStock.dataframe_to_csv(td_sell, "TD")

        all_buy_sell = pd.concat([nn_buy_df, nn_sell_df, td_buy_df, td_sell_df])

        all_buy_sell.columns = ['Date', 'Code', 'Value', 'Source']
        all_buy_sell['Date'] = [EasyStock.format_all_buy_sell_date(l) for l in all_buy_sell['Date']]
        all_buy_sell['Value'] = pd.to_numeric(all_buy_sell['Value'])
        all_buy_sell.index.name = 'id'
        if save:
            all_buy_sell.to_csv("data/" + "KLMB.csv", sep=',')
            all_buy_sell.to_csv("data/" + last_day + "_BS.csv", sep=',')
        return all_buy_sell


if __name__ == '__main__':
    print("Processing EasyStock Data")
    print("By TrungMC@gmail.com")
    pd.options.mode.chained_assignment = None
    data = EasyStock.read_gsheet_data()
    ps = EasyStock.get_derevative_df(data, save=True)
    cs = EasyStock.get_transaction_df(data, save=True)
    bs = EasyStock.get_top_buy_sell(data, save=True)
    print(bs)
    print("Done")
