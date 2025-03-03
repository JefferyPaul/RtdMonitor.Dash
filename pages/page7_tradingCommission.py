import os
from datetime import datetime, timedelta, date
import json
from typing import Dict, List
import logging

import pandas as pd
import dash
from dash import Dash, dcc, html, Input, Output, callback
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

dash.register_page(
    __name__,
    name='Commission'
)


# =====================    参数配置   ============================= #


P_DATA_ROOT = r'Z:\Anthony\TradingCommission@Jeffery'
logger = logging.getLogger('page7')


def wrapped_gen_trade_date(l_all_date: list):
    l_all_date.sort()
    d_next_date = dict()
    for n, _d in enumerate(l_all_date[:-1]):
        d_next_date[_d] = l_all_date[n+1]
    d_next_date[l_all_date[-1]] = (datetime.strptime(l_all_date[-1], '%Y%m%d') + timedelta(days=1)).strftime('%Y%m%d')

    def gen_trade_date(s: str):
        s_d, s_t = s.split(' ')
        if int(s_t[:2]) > 16:
           return d_next_date[s_d]
        else:
            return s_d

    return gen_trade_date


# 读取数据
D_ALL_DATA_DF_COMMISSION: Dict[str, pd.DataFrame] = dict()
for _file_name in os.listdir(P_DATA_ROOT):
    _p_file = os.path.join(P_DATA_ROOT, _file_name)
    _item_name = _file_name[:-4]
    if not os.path.isfile(_p_file):
        continue
    _df = pd.read_csv(_p_file, names=['DateTime', 'Ticker', 'LongShort', 'Volume', 'Price', 'Commission'])
    # df['Date'] = df['Date'].apply(func=lambda x: datetime.strptime(str(x), '%Y%m%d'))
    _df['DateTime'] = _df['DateTime'].apply(func=lambda x: str(x))
    _df['Date0'] = _df['DateTime'].apply(func=lambda x: x.split(' ')[0])
    _l_all_date = _df['Date0'].unique().tolist()
    _df['Date'] = _df['DateTime'].apply(func=wrapped_gen_trade_date(_l_all_date))
    _df['Commission'] = _df['Commission'].round(0)
    D_ALL_DATA_DF_COMMISSION[_item_name] = _df

L_ALL_DATA_DF_NAME_COMMISSION = list(D_ALL_DATA_DF_COMMISSION.keys())
L_ALL_DATA_DF_NAME_COMMISSION.sort(key=lambda x: x.lower())
L_ALL_DATA_DF_NAME_COMMISSION_HEAD = [_ for _ in L_ALL_DATA_DF_NAME_COMMISSION if _[0] == '_']


# ===============================                   ===============================


# 页面布局
def layout():
    _ = html.Div(children=[
            # 选择 策略
            html.Div(
                children=[
                    html.H6('( T+1 08:00 更新 )'),  # 标题
                    '选择策略/产品：',
                    dcc.Dropdown(
                        L_ALL_DATA_DF_NAME_COMMISSION,
                        value=L_ALL_DATA_DF_NAME_COMMISSION_HEAD,
                        # value=L_ALL_DATA_DF_NAME_COMMISSION[0],
                        id='fund_name-commission',
                        multi=True,
                        clearable=False
                    ),
                ],
                style={'width': '10%', 'display': 'inline-block'},
            ),
            dcc.Graph(id='graph-commission'),
        ])

    return _


# =====================    dash操作  ============================= #
# 【1】
# Multiple components can update everytime interval gets fired.
@callback(
    Output(component_id='graph-commission', component_property='figure'),
    Input(component_id='fund_name-commission', component_property='value')
)
def get_fund_graph_commission(l_fund_name):
    if type(l_fund_name) == str:
        l_fund_name = [l_fund_name]

    logger.info('in update_graph_in_interval()')
    l_df = list()
    for fund_name in l_fund_name:
        df: pd.DataFrame = D_ALL_DATA_DF_COMMISSION.get(fund_name).copy()
        df_2 = df[['Date', 'Ticker', 'Commission']]
        df_2 = df_2.set_index(['Date', 'Ticker'])
        grouped_date = df_2.groupby('Date')
        grouped_date_sum = grouped_date.sum()
        grouped_date_sum.rename(columns={'Commission': fund_name}, inplace=True)
        l_df.append(grouped_date_sum)
    df_all = pd.concat(l_df, axis=1)

    return _gen_fig_commission(df_all, fig_title='每日佣金', width=1000, height=500)


# 生成 信号持仓图
def _gen_fig_commission(df: pd.DataFrame, fig_title: str, width=1000, height=400):
    l_index_sorted_by_value = df.index.to_list()
    l_columns = df.columns.to_list()
    fig = go.Figure()

    if len(l_columns) == 0:
        return fig

    _max_y = 0
    # _max_y = max([max(df.values), abs(min(df.values))])

    for ticker in l_columns:
        y = list(df.loc[:, ticker].values).copy()
        if max(y) > _max_y:
            _max_y = max(y)

        fig.add_trace(
            go.Scatter(
                x=l_index_sorted_by_value,
                y=y,
                mode='lines',
                # line_shape='vh',        # https://plotly.com/python/line-charts/   阶梯图
                # line_shape='hvh',        # https://plotly.com/python/line-charts/   阶梯图
                name=ticker,
                line=dict(
                    width=1,
                ),
            ))
        if len(y) == 0:
            continue
        # _max_y_new = max([abs(_) for _ in y])
        # # print(_max_y_new, _max_y, trader)
        # if _max_y_new > _max_y:
        #     _max_y = _max_y_new
    # _y_size = round((_max_y * 1.1), -len(str(int(_max_y))) + 2)

    fig.update_xaxes(
        # x轴名称
        # title_font=dict(size=16, family='Courier', color='crimson'),
        # ticktext=l_index_sorted_by_value,
        # 轴线
        showline=True,
        linecolor='black',
        linewidth=1,
        mirror=True,  # 对称的轴线，上边线
        # 标签
        # type='category',
        # categoryorder='array',
        # categoryarray=l_index_sorted_by_value,
        # ticks='inside',
        tickwidth=1,
        tickfont=dict(
            size=10
        ),
        # ticklen=10,
        # tickcolor='red',
        # tickmode='array',
        # tickvals=l_index_sorted_by_value,
        # ticktext=l_index_sorted_by_value,
        tickangle=-90,
        # 网格线
        showgrid=True,
        gridwidth=0.5,
        gridcolor='gray',
        # gridcolor='Black',
        griddash='dot',
        # zeroline=True,
        # zerolinecolor='black',
        # zerolinewidth=1.5,
    )
    fig.update_yaxes(
        showline=True,
        linecolor='black',
        linewidth=0.5,
        mirror=True,
        title='',
        # 网格线
        showgrid=True,
        gridwidth=1,
        gridcolor='gray',
        griddash='dot',
        # zeroline=True,
        zeroline=True,
        zerolinecolor='black',
        zerolinewidth=1,
    )

    # _yaxis_max = int(_max_y) + 1
    fig.update_layout(
        # paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',  # 设置背景色为白色
        width=width,
        height=height,
        title=dict(
            text=fig_title,
            font=dict(size=14),
            y=1,  # 位置，坐标轴的长度看做1
            x=0.5,
            xanchor='center',
            yanchor='top',
        ),
        # margin=dict(l=40, r=0, t=40, b=30),
        margin=dict(l=0, r=0, t=20, b=50),
        # yaxis_range=[-_y_size, _y_size],
        # yaxis_range=[0, _yaxis_max],
        # 图例位置
        legend=dict(
            # orientation="h",  # 开启水平显示
            # yanchor="bottom",  # y轴顶部  bottom top
            # y=0,
            # xanchor="left",  # x轴靠左
            # 3=0,
            # itemsizing='trace',   # trace 和 constant 两种设置, trace 小图形
            font=dict(size=10),
            traceorder="normal",
        ),
    )
    # fig.update_traces(hoverinfo='text+name', mode='lines+markers')
    fig.update_traces(mode='lines+markers')

    return fig

