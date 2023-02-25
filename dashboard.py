import streamlit as st
import pandas as pd
import altair as alt

from main import EasyStock

st.set_page_config(page_title="TKGG by TrungMC", layout="wide")


@st.cache_data
def update_data():

    pd.options.mode.chained_assignment = None

    data = EasyStock.read_gsheet_data()
    ps = EasyStock.get_derevative_df(data)
    cs = EasyStock.get_transaction_df(data)
    bs = EasyStock.get_top_buy_sell(data)
    return ps, cs, bs


# @st.cache_data
# def load_derevative_data():
#     derevative_df = pd.read_csv('./data/KLGDPS.csv')
#     return derevative_df
#
#
# @st.cache_data
# def load_stock_data():
#     stock_df = pd.read_csv('./data/KLGDCS.csv')
#     return stock_df
#
#
# @st.cache_data
# def load_buysell_data():
#     buysell_df = pd.read_csv('./data/KLMB.csv')
#     return buysell_df

ps, cs, bs = update_data()


def create_page():
    header = st.container()
    dataset = st.container()

    stock_container = st.container()
    st.title("Thống kê giao dịch by TrungMC")

    if st.button("Update Data"):
        st.cache_data.clear()
        update_data()

    tab1, tab2, tab3 = st.tabs(["PS", "CS", "Hot Stocks"])
    with tab1:
        df = ps[['Date', 'CN_Net', 'TD_Net', 'NN_Net']].sort_values(by=['Date'])
        oi_df = ps[['Date', 'Open_Interest']]
        with tab1.container():
            der1, der2 = st.columns(2)
            ps1 = pd.melt(df, id_vars=['Date'], value_vars=['CN_Net', 'TD_Net', 'NN_Net'])

            with der1:
                der1.subheader("Khối lượng giao dịch hàng ngày")
                ps_tran_chart = alt.Chart(ps1, height=900).mark_line(point=True, strokeWidth=5).encode(
                    x='Date',
                    y='value',
                    color='variable'
                )
                der1.altair_chart(ps_tran_chart, use_container_width=True)
            with der2:
                der2.subheader("Khối lượng giao dịch lũy kế")
                ps_cum_chart = alt.Chart(ps1, height=900).mark_line(point=True, strokeWidth=5).transform_window(
                    sort=[{'field': 'Date'}],
                    cummulative_net='sum(value)',
                    groupby=['variable'],
                ).encode(
                    x='Date',
                    y='cummulative_net:Q',
                    color='variable'
                )
                oi_chart = alt.Chart(oi_df).mark_bar(color="#FFAA00").encode(x='Date', y='Open_Interest')

                der2.altair_chart(alt.layer(oi_chart,ps_cum_chart, ), use_container_width=True)



    with tab2:
        cs_df = cs[['Date', 'NDTNN( Tỷ VND)', 'Cá Nhân TN ( Tỷ VND)', 'Tự Doanh( Tỷ VND)']].sort_values(by=['Date'])
        cs_df_cumsum = cs_df.sort_values(by=['Date'])
        cs_df_cumsum['NDTNN( Tỷ VND)'] = cs_df_cumsum["NDTNN( Tỷ VND)"].cumsum()
        cs_df_cumsum['Cá Nhân TN ( Tỷ VND)'] = cs_df_cumsum["Cá Nhân TN ( Tỷ VND)"].cumsum()
        cs_df_cumsum['Tự Doanh( Tỷ VND)'] = cs_df_cumsum["Tự Doanh( Tỷ VND)"].cumsum()

        stock1, stock2 = tab2.columns(2)
        with stock1:
            st.subheader("KLMB")
            st.bar_chart(cs_df, x='Date', height=900)
        with stock2:
            st.subheader("KLMB Lũy kế")
            st.line_chart(cs_df_cumsum, height=900, x='Date',
                          y=['NDTNN( Tỷ VND)', 'Cá Nhân TN ( Tỷ VND)', 'Tự Doanh( Tỷ VND)'])

    with tab3:
        buysell_df = bs

        buysell1, buysell2 = tab3.columns(2)
        with buysell1:
            chart = alt.Chart(buysell_df, height=900).mark_bar(
                opacity=1,

            ).encode(
                x=alt.X('Code'),
                y=alt.Y('Value'),
                color=alt.Color('Source')
            ).configure_view()
            st.altair_chart(chart)


if __name__ == '__main__':
    print("Processing EasyStock Data")
    print("By TrungMC@gmail.com")
    create_page()
    print("Done")
