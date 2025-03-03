import os
import sys
from datetime import datetime, timedelta, date
import json
from typing import Dict, List
import logging

import pandas as pd
import dash
from dash import Dash, dcc, html, Input, Output, callback, State
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from cache_config import configure_cache


dash.register_page(
    __name__,
    name='test'
)


# =====================    参数配置   ============================= #

P_DATA_ROOT = r'C:\D\_workspace_A2\AGP.RtdMonitor\AGP.TradingReview.HoldingPositionAnalysis\__PositionValue_Concat'
# 设置缓存
TIMEOUT = 60 * 60   # 缓存时间（秒）


# ===============================                   ===============================


# 页面布局
layout = html.Div(children=[
    # 选择 策略
    html.Div(
        children=[            
            html.H6('( T+1 09:50 更新 )'),  # 标题
            '选择策略/产品：',
            dcc.Dropdown(
                id='funds-dropdown',
                clearable=False
            ),
        ],
        style={'width': '10%', 'display': 'inline-block'},
    ),
    dcc.Graph(id='fund-graph'),

    dcc.Interval(
        # 定时器
        id='interval-component-read-data',
        interval=1000 * TIMEOUT,  # in milliseconds
        n_intervals=0
    ),
    dcc.Store(id='data-store')      # 用于储存数据的隐藏组件


    # dbc.Row(
    #     children=[
    #         dbc.Col(dcc.Graph(id='graph-1')),
    #     ],
    # ),
    # dbc.Row(
    #     children=[
    #         dbc.Col(dcc.Graph(id='position-graph-PA')),
    #     ],
    # ),

    # html.Br(),
    # dbc.Col(dcc.Textarea(id='data-time')),
    # dcc.Interval(
    #     # 定时器，60秒
    #     id='interval-component-read-all-data',
    #     interval=1000 * 60 * 60,  # in milliseconds
    #     n_intervals=0
    # ),
])

# =====================    dash操作  ============================= #


def _get_latest_data():
    # 读取数据
    d_all_data: Dict[str, dict] = dict()
    for _file_name in os.listdir(P_DATA_ROOT):
        _p_file = os.path.join(P_DATA_ROOT, _file_name)
        _item_name = _file_name[:-4]
        if not os.path.isfile(_p_file):
            continue
        _df = pd.read_csv(_p_file, names=['Date', 'Ticker', 'NetValue', 'LongValue', 'ShortValue'])
        # df['Date'] = df['Date'].apply(func=lambda x: datetime.strptime(str(x), '%Y%m%d'))
        _df['Date'] = _df['Date'].apply(func=lambda x: str(x))
        d_all_data[_item_name] = _df.to_dict('records')
    return d_all_data


# 生成 信号持仓图
def _gen_fig(df: pd.DataFrame, fig_title: str, width=1000, height=400):
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


def init_callbacks(app):
    cache = configure_cache(app)

    @cache.memoize(timeout=TIMEOUT)
    def get_latest_data_with_cache():
        return _get_latest_data()

    @callback(
        Output('data-store', 'data'),
        Output('funds-dropdown', 'options'),
        Output('funds-dropdown', 'value'),
        Input(component_id='interval-component-read-data', component_property='n_intervals'),
    )
    def update_data(n):
        print(f'in update_data(), {n}')
        _data: Dict[str, pd.dict] = get_latest_data_with_cache()
        _keys = list(_data.keys())
        _keys.sort(key=lambda x: x.lower())
        return _data, _keys, _keys[0]

    @callback(
        Output('fund-graph', 'figure'),
        Input('funds-dropdown', 'value'),
        State('data-store', 'data')
    )
    def get_fund_graph(fund_name, data: Dict[str, pd.DataFrame]):
        fund_data: dict or None = data.get(fund_name)
        if not fund_data:
            return _gen_fig(pd.DataFrame({}), fig_title='', width=1000, height=500)
        df = pd.DataFrame(fund_data)
        df_2 = df.set_index(['Date', 'Ticker'])
        grouped_date = df_2.groupby('Date')
        grouped_date_sum = grouped_date.sum()

        return _gen_fig(grouped_date_sum, fig_title=fund_name, width=1000, height=500)
