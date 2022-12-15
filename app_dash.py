from datetime import datetime
import json

import pandas as pd
import numpy as np
import dash
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go


D_LIVE_POSITION_FILE_PATH = {
    "aio": {
        "data": r'..\Data\OmsLivePosition\_Output_3_PositionPInitX\AIO\data.csv',
        "update": r'..\Data\OmsLivePosition\_Output_3_PositionPInitX\AIO\_update.csv',
        "sort": "JuLi2"
    },
    "selected": {
        "data": r'..\Data\OmsLivePosition\_Output_3_PositionPInitX\Selected\data.csv',
        "update": r'..\Data\OmsLivePosition\_Output_3_PositionPInitX\Selected\_update.csv',
        "sort": "QinMo"
    }
}

D_ACTIVATE_TICKER_PATH = {
    "ticker_changed": r"..\Data\SignalTickerChanged\data.json"
}

# Test
# D_LIVE_POSITION_FILE_PATH = {
#     "aio": {
#         "data": r'D:\_workspace\alphasys\AlphaSysGuardingPlatform\TradingServer'
#                 r'\_DailyCheck.4.AGP.OMS.LivePositionViewer\OMS.LivePosition.DataHandler'
#                 r'\_Output_3_PositionPInitX\AIO\data.csv',
#         "update": r'D:\_workspace\alphasys\AlphaSysGuardingPlatform\TradingServer'
#                   r'\_DailyCheck.4.AGP.OMS.LivePositionViewer\OMS.LivePosition.DataHandler'
#                   r'\_Output_3_PositionPInitX\AIO\_update.csv',
#         "sort": "JuLi2"
#     },
#     "selected": {
#         "data": r'D:\_workspace\alphasys\AlphaSysGuardingPlatform\TradingServer'
#                 r'\_DailyCheck.4.AGP.OMS.LivePositionViewer\OMS.LivePosition.DataHandler'
#                 r'\_Output_3_PositionPInitX\Selected\data.csv',
#         "update": r'D:\_workspace\alphasys\AlphaSysGuardingPlatform\TradingServer'
#                   r'\_DailyCheck.4.AGP.OMS.LivePositionViewer\OMS.LivePosition.DataHandler'
#                   r'\_Output_3_PositionPInitX\Selected\_update.csv',
#         "sort": "ShengShi8"
#     }
# }
# D_ACTIVATE_TICKER_PATH = {
#     "ticker_changed": "r"
# }


app = dash.Dash(
    __name__,
    # external_stylesheets=external_stylesheets
)
app.layout = html.Div(children=[
    # 产品持仓对比图
    html.Div(children=[
        html.H3('Product Live Holding Positions'),
        dcc.Graph(id='graph-aio'),
        dcc.Graph(id='graph-selected'),
        dcc.Interval(
            id='interval-component-position-graph',
            interval=20*1000,    # in milliseconds          20s
            n_intervals=0
        ),
    ]),
    html.Br(),
    html.Div(children=[
        html.H3("Signal-HoldingTickerChanged-Check"),
        html.Div(id='activate-tickers-check'),
        dcc.Interval(
            id='interval-component-activate-tickers-check',
            interval=60*5*1000,    # in milliseconds       5min
            n_intervals=0
        )
    ]),
])

# 【1】
# Multiple components can update everytime interval gets fired.
@app.callback(
    Output('graph-aio', 'figure'),
    Output('graph-selected', 'figure'),
    Input('interval-component-position-graph', 'n_intervals'))
def interval_update_position_graph(n):
    l_output = []
    for name, info in D_LIVE_POSITION_FILE_PATH.items():
        p_data = info['data']
        p_update = info['update']
        sort_by = info['sort']

        # 数据更新时间
        data_update_dt: datetime = _get_position_update_time(p_update)
        # pivot data
        df = _get_position_data(p_data, sort_by)
        l_columns = df.columns.to_list()
        fig_title = f"{name} _ {str(len(l_columns))} _ {data_update_dt.strftime('%H:%M:%S')}"
        fig = _gen_position_fig(df, fig_title)
        print(fig_title)
        l_output.append(fig)
    return l_output


def _get_position_data(p, sort_by='') -> pd.DataFrame:
    df = pd.read_csv(p, names=['ticker', 'trader', 'value'])
    df = df.pivot_table(values='value', index='ticker', columns='trader', aggfunc='sum')
    df = df.fillna(0)     # 补零
    df = df.loc[(df != 0).any(axis=1), :]    # 去除volume 全是0的 ticker
    # print(df)

    # 按照 Ticker 量排序
    l_column_names = list(df.columns)
    if sort_by not in l_column_names:
        l_index_sorted_by_value = list(df.T.sum().sort_values().to_dict().keys())
    else:
        l_index_sorted_by_value = df.loc[:, sort_by].sort_values().index.to_list()

    df = df.reindex(l_index_sorted_by_value)
    # df = df.stack().reset_index()
    # df.columns = ['ticker', 'trader', 'value']
    # print(df.head())
    return df


def _get_position_update_time(p) -> datetime:
    with open(p) as f:
        line = f.readlines()
    line = line[0].strip()
    return datetime.strptime(line, '%Y%m%d %H%M%S')


def _gen_position_fig(df: pd.DataFrame, fig_title: str):
    l_index_sorted_by_value = df.index.to_list()
    l_columns = df.columns.to_list()
    fig = go.Figure()
    for trader in l_columns:
        y = list(df.loc[:, trader].values)
        fig.add_trace(
            go.Scatter(
                x=l_index_sorted_by_value, y=y,
                mode='lines',
                name=trader,
                line=dict(
                    width=1,
                ),
            ))

    fig.update_xaxes(
        # x轴名称
        # title_font=dict(size=16, family='Courier', color='crimson'),
        # ticktext=l_index_sorted_by_value,
        # 轴线
        showline=True,
        linecolor='black',
        linewidth=1,
        mirror=True,        # 对称的轴线，上边线
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
    fig.update_layout(
        # paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',       # 设置背景色为白色
        # width=1000,
        height=300,
        title=dict(
            text=fig_title,
            font=dict(size=18),
            y=1,      # 位置，坐标轴的长度看做1
            x=0.5,
            xanchor='center',
            yanchor='top',
        ),
        # margin=dict(l=40, r=0, t=40, b=30),
        margin=dict(l=0, r=0, t=20, b=50),
    )
    return fig


# 【2】
@app.callback(
    Output(component_id='activate-tickers-check', component_property='children'),
    Input('interval-component-activate-tickers-check', 'n_intervals'))
def interval_update_activate_tickers_check(n):
    path_ticker_changed = D_ACTIVATE_TICKER_PATH['ticker_changed']
    d_ticker_changed_info = json.loads(open(path_ticker_changed).read())
    _new_tickers = d_ticker_changed_info['new_tickers']
    _flatted_tickers = d_ticker_changed_info['flatted_tickers']
    _new_file = d_ticker_changed_info['new_file']
    _old_file = d_ticker_changed_info['old_file']
    _update_time = d_ticker_changed_info['update_time']
    _new_data_time = d_ticker_changed_info['new_data_time']
    return f'NewTickers: {",".join(_new_tickers)}  OldTickers: {",".join(_flatted_tickers)}  UpdateTime: {_update_time}'


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True)
