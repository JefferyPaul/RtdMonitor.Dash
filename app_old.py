import os.path
from datetime import datetime
import json

import pandas as pd
import numpy as np
import dash
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go


# =====================    参数配置   ============================= #
# [1] 信号持仓配置
D_LIVE_POSITION_FILE_PATH = {
    "aio": {
        "data": r'..\Data\OmsLivePosition\_Output_3_PositionPInitX\AIO\data.csv',
        "update": r'..\Data\OmsLivePosition\_Output_3_PositionPInitX\AIO\_update.csv',
        "sort": "JuLi2"
    },
    "selected": {
        "data": r'..\Data\OmsLivePosition\_Output_3_PositionPInitX\Selected\data.csv',
        "update": r'..\Data\OmsLivePosition\_Output_3_PositionPInitX\Selected\_update.csv',
        "sort": "ShengShi8"
    }
}

# [2]
D_SIGNAL_ACTIVATE_TICKER_PATH = {
    "ticker_changed": r"..\Data\SignalTickerChanged\data.json"
}

# [3] BarData 换月
L_BARDATA_ACTIVATE_TICKER_INFO_PATH = [
    {
        "name": "主力合约换月",
        "path": r"..\Data\MostActivateTickers\_MostActivateTickers_1_Today_Result.csv",
    },
    {
        "name": "远月合约换月",
        "path": r"..\Data\MostActivateTickers\_MostActivateTickers_2Longer_Today_Result.csv",
    },
]


# =====================    dash 布置  ============================= #
app = dash.Dash(
    __name__,
    # external_stylesheets=external_stylesheets
)
app.layout = html.Div(children=[
    # [1] 产品持仓对比图
    html.Div(children=[
        html.H3('Product Live Holding Positions'),      # 标题
        dcc.Graph(id='graph-aio'),                      # 图1，aio的持仓
        dcc.Graph(id='graph-selected'),                 # 图2，selected的持仓
        dcc.Interval(                                   # 定时器，60秒
            id='interval-component-position-graph',
            interval=1000*60,    # in milliseconds
            n_intervals=0
        ),
    ]),
    html.Br(),
    # [2] AIO信号的持仓ticker变化（合约换月）
    html.Div(children=[
        html.H3("AIO信号换月"),   # 标题
        html.Div(id='signal-activate-tickers-check'),          # 输出，
        dcc.Interval(                                   # 定时器，5分钟
            id='interval-component-activate-tickers-check',
            interval=1000*60*5,
            n_intervals=0
        )
    ]),
    # [3] DSBarData-MostActivateTickers 变化
    html.Div(children=[
        html.H3("Bar数据检查-主力合约变更"),          # 标题
        html.Div(id="bardata-activate-tickers-check"),  # 输出
        dcc.Interval(                                   # 定时器，2小时
            id='interval-component-bardata-activate-tickers-check',
            interval=1000*60*60*2,
            n_intervals=0,
        )
    ])
])


# =====================    dash操作  ============================= #
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


# 获取 信号持仓数据
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


# 获取 信号持仓的 更新时间
def _get_position_update_time(p) -> datetime:
    with open(p) as f:
        line = f.readlines()
    line = line[0].strip()
    return datetime.strptime(line, '%Y%m%d %H%M%S')


# 生成 信号持仓图
def _gen_position_fig(df: pd.DataFrame, fig_title: str):
    l_index_sorted_by_value = df.index.to_list()
    l_columns = df.columns.to_list()
    fig = go.Figure()
    _max_y = 0
    for trader in l_columns:
        y = list(df.loc[:, trader].values).copy()
        fig.add_trace(
            go.Scatter(
                x=l_index_sorted_by_value, 
                y=y,
                mode='lines',
                name=trader,
                line=dict(
                    width=1,
                ),
            ))
        _max_y_new = max([abs(_) for _ in y])
        if _max_y_new > _max_y:
            _max_y = _max_y_new
    _y_size = round((_max_y * 1.1), -(int(_max_y * 1.5) % 10)+2)

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
        yaxis_range=[-_y_size, _y_size],
    )
    return fig


# 【2】 AIO信号的持仓ticker变化（合约换月）
@app.callback(
    Output(component_id='signal-activate-tickers-check', component_property='children'),
    Input('interval-component-activate-tickers-check', 'n_intervals'))
def interval_update_activate_tickers_check(n):
    path_ticker_changed = D_SIGNAL_ACTIVATE_TICKER_PATH['ticker_changed']
    d_ticker_changed_info = json.loads(open(path_ticker_changed).read())
    _new_tickers = d_ticker_changed_info['new_tickers']
    _flatted_tickers = d_ticker_changed_info['flatted_tickers']
    _new_file = d_ticker_changed_info['new_file']
    _old_file = d_ticker_changed_info['old_file']
    _update_time = datetime.strptime(
        d_ticker_changed_info['update_time'], '%Y%m%d %H%M%S').strftime('%Y-%m-%d %H:%M:%S')
    _new_data_time = d_ticker_changed_info['new_data_time']
    if _new_tickers or _flatted_tickers:
        if _new_tickers:
            _new_tickers.sort()
        if _flatted_tickers:
            _flatted_tickers.sort()
            
        return [
            f'新上合约: {", ".join(_new_tickers)}',
            html.Br(),
            f'下线合约:  {", ".join(_flatted_tickers)}',
            html.Br(),
            f'UpdateTime: {_update_time}'
        ]
    else:
        return [
            f'UpdateTime: {_update_time}'
        ]


# 【3】 AIO信号的持仓ticker变化（合约换月）
@app.callback(
    Output(component_id='bardata-activate-tickers-check', component_property='children'),
    Input('interval-component-bardata-activate-tickers-check', 'n_intervals'))
def interval_update_bardata_activate_tickers_check(n):
    if not L_BARDATA_ACTIVATE_TICKER_INFO_PATH:
        return ''

    l_all_output = []
    for info in L_BARDATA_ACTIVATE_TICKER_INFO_PATH:
        l_output = []
        name = info['name']
        file_path = info['path']
        if not os.path.isfile(file_path):
            print('找不到此文件,%s' % file_path)
            continue
        with open(file_path) as f:
            l_lines = f.readlines()
        for line in l_lines:
            line = line.strip()
            if line == '':
                continue
            l_output.append((line.split(',')[2]))
        if l_output:
            l_all_output.append(f"{name}: {','.join(l_output)}")
            l_all_output.append(html.Br())

    mdt = datetime.fromtimestamp(os.path.getmtime(L_BARDATA_ACTIVATE_TICKER_INFO_PATH[0]['path']))
    l_all_output.append(f'UpdateTime: {mdt.strftime("%Y-%m-%d %H:%M:%S")}')
    return l_all_output


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port='8050', debug=True)
