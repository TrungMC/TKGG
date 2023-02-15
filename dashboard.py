import streamlit as st
import pandas as pd
import altair as alt

from main import EasyStock

def update_data():
    data = EasyStock.read_gsheet_data()
    ps = EasyStock.get_derevative_df(data)
    cs = EasyStock.get_transaction_df(data)
    bs = EasyStock.get_top_buy_sell(data)

@st.cache_data
def load_derevative_data():
    derevative_df = pd.read_csv('C:/Users/trung/PycharmProjects/TKGG/data/KLGDPS.csv')
    return derevative_df


@st.cache_data
def load_stock_data():
    stock_df = pd.read_csv('C:/Users/trung/PycharmProjects/TKGG/data/KLGDCS.csv')
    return stock_df


@st.cache_data
def load_buysell_data():
    buysell_df = pd.read_csv('C:/Users/trung/PycharmProjects/TKGG/data/KLMB.csv')
    return buysell_df


st.set_page_config(page_title="TKGG by TrungMC", layout="wide")
header = st.container()
dataset = st.container()

stock_container = st.container()
st.title("Thống kê giao dịch by TrungMC")
tab1, tab2, tab3 = st.tabs(["PS", "CS", "Hot Stocks"])
with tab1:
    df = load_derevative_data().sort_values(by=['Date'])
    df_cumsum = df.sort_values(by=['Date'])
    df_cumsum['CN_Net'] = df["CN_Net"].cumsum()
    df_cumsum['TD_Net'] = df["TD_Net"].cumsum()
    df_cumsum['NN_Net'] = df["NN_Net"].cumsum()

    derevative_container = tab1.container()
    with derevative_container:
        der1, der2 = derevative_container.columns(2)

        with der1:
            der1.subheader("Khối lượng giao dịch hàng ngày")
            der1.line_chart(df, x='Date', y=['CN_Net', 'TD_Net', 'NN_Net'])
        with der2:
            der2.subheader("Khối lượng giao dịch lũy kế")
            der2.line_chart(df_cumsum, x='Date', y=['CN_Net', 'TD_Net', 'NN_Net'])
with tab2:
    cs_df = load_stock_data().sort_values(by=['Date'])
    cs_df_cumsum = cs_df.sort_values(by=['Date'])
    cs_df_cumsum['NDTNN( Tỷ VND)'] = cs_df_cumsum["NDTNN( Tỷ VND)"].cumsum()
    cs_df_cumsum['Cá Nhân TN ( Tỷ VND)'] = cs_df_cumsum["Cá Nhân TN ( Tỷ VND)"].cumsum()
    cs_df_cumsum['Tự Doanh( Tỷ VND)'] = cs_df_cumsum["Tự Doanh( Tỷ VND)"].cumsum()

    stock1, stock2 = tab2.columns(2)
    with stock1:
        st.subheader("KLMB")
        st.bar_chart(cs_df, x='Date', y=['NDTNN( Tỷ VND)', 'Cá Nhân TN ( Tỷ VND)', 'Tự Doanh( Tỷ VND)'])
    with stock2:
        st.subheader("KLMB Lũy kế")
        st.line_chart(cs_df_cumsum, x='Date', y=['NDTNN( Tỷ VND)', 'Cá Nhân TN ( Tỷ VND)', 'Tự Doanh( Tỷ VND)'])

with tab3:
    buysell_df = load_buysell_data()

    buysell1, buysell2 = tab3.columns(2)
    with buysell1:
        chart=alt.Chart(buysell_df).mark_bar(
            opacity=1,
        ).encode(

            x=alt.X('Code'),
            y=alt.Y('Value'),
            color=alt.Color('Source')
        ).configure_view(stroke='transparent')
        st.altair_chart(chart)
