from datetime import datetime, timedelta, date
import json

import pandas as pd
import dash
from dash import Dash, dcc, html, Input, Output, callback
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

dash.register_page(
    __name__,
    name='CancelRate'
)

# =====================    参数配置   ============================= #
D_DATA_FILE = {
    "D1": r"Z:\Anthony\FillRate_concat@Jeffery\1.csv",
    "D7": r"Z:\Anthony\FillRate_concat@Jeffery\7.csv"
}


# 页面布局
def layout():
    _ = html.Div(
        children=[
            # [1] 产品实时持仓对比图
            html.H4('下单量/成交量'),  # 标题
            html.H5('每日 21:05 更新; 刻度1.5 代表 slippage=0'),  # 标题
            html.Div(
                children=[
                    dbc.Row(
                        children=[
                            dbc.Col(dcc.Graph(id='graph-cancel-rate-1')),
                            dbc.Col(dcc.Graph(id='graph-cancel-rate-2')),
                        ],
                    ),
                    # dbc.Row(
                    #     children=[
                    #         dbc.Col(dcc.Graph(id='position-graph-PA')),
                    #     ],
                    # ),
                    dcc.Interval(
                        # 定时器，60秒
                        id='interval-component-position-graph',
                        interval=1000 * 60 * 10,  # in milliseconds
                        n_intervals=0
                    ),
                ],
            ),

            html.Br(),
        ]
    )
    return _


# =====================    dash操作  ============================= #
# 【1】
# Multiple components can update everytime interval gets fired.
@callback(
    Output(component_id='graph-cancel-rate-1', component_property='figure'),
    Output(component_id='graph-cancel-rate-2', component_property='figure'),
    Input(component_id='interval-component-position-graph', component_property='n_intervals'))
def update_graph_in_interval(n):
    l_figs = list()
    for _key in D_DATA_FILE.keys():
        p_data_file = D_DATA_FILE[_key]
        # read data
        df = pd.read_csv(p_data_file, names=['Date', 'Ticker', 'FillRate'])
        # df['Date'] = df['Date'].apply(func=lambda x: datetime.strptime(str(x), '%Y%m%d'))
        df['Date'] = df['Date'].apply(func=lambda x: str(x))
        # df['CancelRate'] = 1 - df['FillRate']
        # 最小值是1, 大于2 代表 slippage 较大
        df['CancelRate'] = 1 / df['FillRate']
        df = df.pivot_table(values='CancelRate', index='Date', columns='Ticker', aggfunc='mean')
        # df = df.fillna('bfill')

        # 筛选 排序
        l_columns = df.columns.to_list().copy()
        l_columns_selected_sorted = list()
        l_columns_selected = list()
        for ticker in l_columns:
            _d_ticker_data = df.loc[:, ticker].to_dict()
            # 去除 nan
            _d_ticker_data = {
                _date: _v
                for _date, _v in _d_ticker_data.items()
                if _v >= 0
            }
            if len(_d_ticker_data) == 0:
                continue
            # 去除 每一天都小于 0.5 的情况
            # if len([_ for _ in _d_ticker_data.values() if _ < 2]) == 0:
            #     continue
            _last_date = max(_d_ticker_data.keys())
            _last_value = _d_ticker_data[_last_date]
            l_columns_selected_sorted.append([ticker, (_last_date, _last_value)])
        l_columns_selected_sorted.sort(key=lambda x: x[1], reverse=True)
        l_columns_selected = [_[0] for _ in l_columns_selected_sorted]

        fig = _gen_cancel_rate_fig(df.loc[:, l_columns_selected], fig_title=_key, width=700, height=800)
        l_figs.append(fig)
        print(f'update graph, {_key}')

    #
        # l_position_figs.append(fig)
    # return l_position_figs
    return l_figs


# 生成 信号持仓图
def _gen_cancel_rate_fig(df: pd.DataFrame, fig_title: str, width=1000, height=400):
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
        gridwidth=1,
        gridcolor='gray',
        # gridcolor='Black',
        griddash='dot',
        # zeroline=False,
    )
    fig.update_yaxes(
        showline=True,
        linecolor='black',
        linewidth=1,
        mirror=True,
        title='',
        # 网格线
        showgrid=True,
        gridwidth=1,
        gridcolor='gray',
        griddash='dot',
        zeroline=False,
    )

    _yaxis_max = int(_max_y) + 1
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
        yaxis_range=[0, _yaxis_max],
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
    fig.update_traces(hoverinfo='text+name', mode='lines+markers')

    return fig

