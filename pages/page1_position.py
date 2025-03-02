import os.path
from datetime import datetime, timedelta, date
import json
import logging

logger = logging.getLogger('DashMonitor_LivePosition')

import pandas as pd
import dash
from dash import Dash, dcc, html, Input, Output, callback
import plotly.graph_objects as go
import dash_bootstrap_components as dbc


dash.register_page(
    __name__,
    name='1_LivePosition'
)


# =====================    参数配置   ============================= #
# 【1】 实时持仓 配置
L_POSITION_CHECKING_LIST = ["AIO", "SPA", "PA", "FastTrend", "LongShort"]
D_LIVE_POSITION_FILE_PATH = {
    "AIO": {
        "data": r'..\Data\OmsLivePosition\_Output_3_PositionPInitX\AIO\data.csv',
        "update": r'..\Data\OmsLivePosition\_Output_3_PositionPInitX\AIO\_update.csv',
        "sort": "Paper.AIO"
    },
    "SPA": {
        "data": r'..\Data\OmsLivePosition\_Output_3_PositionPInitX\S8\data.csv',
        "update": r'..\Data\OmsLivePosition\_Output_3_PositionPInitX\S8\_update.csv',
        "sort": "Paper.SPA"
    },
    "PA": {
        "data": r'..\Data\OmsLivePosition\_Output_3_PositionPInitX\PA\data.csv',
        "update": r'..\Data\OmsLivePosition\_Output_3_PositionPInitX\PA\_update.csv',
        "sort": "Paper.PA"
    },
    "FastTrend": {
        "data": r'..\Data\OmsLivePosition\_Output_3_PositionPInitX\FastTrend\data.csv',
        "update": r'..\Data\OmsLivePosition\_Output_3_PositionPInitX\FastTrend\_update.csv',
        "sort": "Paper.FT"
    },
    "LongShort": {
        "data": r'..\Data\OmsLivePosition\_Output_3_PositionPInitX\LongShort\data.csv',
        "update": r'..\Data\OmsLivePosition\_Output_3_PositionPInitX\LongShort\_update.csv',
        "sort": "Paper.LS"
    }
}


# 【3】 持仓合约变更
D_SIGNAL_ACTIVATE_TICKER_PATH = {
    "ticker_changed": r"..\Data\SignalTickerChanged\data.json"
}

# 【4】 BarData 换月
L_BARDATA_ACTIVATE_TICKER_INFO_PATH = [
    {
        "name": "DSBar数据检查 主力合约换月",
        "path": r"..\Data\MostActivateTickers\_MostActivateTickers_1_Today_Result.csv",
    },
    {
        "name": "DSBar数据检查 远月合约换月",
        "path": r"..\Data\MostActivateTickers\_MostActivateTickers_2Longer_Today_Result.csv",
    },
]


# 页面布局
def layout():
    _ = html.Div(
        children=[
            # [1] 产品实时持仓对比图
            html.H6('Live Position'),  # 标题
            html.Div(
                children=[
                    dbc.Row(
                        children=[
                            dbc.Col(dcc.Graph(id='position-graph-AIO'))
                        ],
                    ),
                    dbc.Row(
                        children=[
                            dbc.Col(dcc.Graph(id='position-graph-SPA')),
                            dbc.Col(dcc.Graph(id='position-graph-FastTrend')),
                        ],
                    ),
                    dbc.Row(
                        children=[
                            dbc.Col(dcc.Graph(id='position-graph-PA')),
                            dbc.Col(dcc.Graph(id='position-graph-LongShort')),
                        ],
                    ),
                    dcc.Interval(
                        # 定时器，60秒
                        id='interval-component-position-graph',
                        interval=1000 * 60,  # in milliseconds
                        n_intervals=0
                    ),
                ],
            ),

            # html.H4('实时持仓'),  # 标题
            # # 排版方式 2：
            # # html.Div(
            # #     children=[
            # #         html.Div(dcc.Graph(id='position-graph-AIO')),
            # #         html.Div(
            # #             children=[
            # #                 dcc.Graph(id='position-graph-SPA'),
            # #                 dcc.Graph(id='position-graph-FastTrend')
            # #             ],
            # #             style={
            # #                 'display': 'flex',
            # #                 'flex-direction': 'row'
            # #             }
            # #         ),
            # #         html.Div(
            # #             children=[
            # #                 dcc.Graph(id='position-graph-PA'),
            # #                 dcc.Graph(id='position-graph-LongShort')
            # #             ],
            # #             style={
            # #                 'display': 'flex',
            # #                 'flex-direction': 'row'
            # #             }
            # #         ),
            # #         dcc.Interval(  # 定时器，60秒
            # #             id='interval-component-position-graph',
            # #             interval=1000 * 60,  # in milliseconds
            # #             n_intervals=0
            # #         ),
            # #     ],
            # #     style={
            # #         'display': 'flex',
            # #         'flex-direction': 'column'
            # #     }
            # # ),
            html.Br(),

            # [2] AIO信号的持仓ticker变化（合约换月）
            html.Div(
                children=[
                    # html.H4("AIO信号换月"),  # 标题
                    html.Div(id='signal-trading-tickers-check'),  # 输出，
                    dcc.Interval(
                        # 定时器，30分钟
                        id='interval-component-trading-tickers-check',
                        interval=1000 * 60 * 30,
                        n_intervals=0
                    )
                ]
            ),

            # [3] DSBarData-MostActivateTickers 变化
            # 暂停显示
            # html.Div(
            #     children=[
            #         # html.H4("Bar数据检查-主力合约变更"),  # 标题
            #         html.Div(id="bardata-activate-tickers-check"),  # 输出
            #         dcc.Interval(
            #             # 定时器，2小时
            #             id='interval-component-bardata-activate-tickers-check',
            #             interval=1000 * 60 * 60 * 2,
            #             n_intervals=0,
            #         )
            #     ]
            # )
        ]
    )
    return _


# =====================    dash操作  ============================= #
# 【1】
# Multiple components can update everytime interval gets fired.
@callback(
    Output(component_id='position-graph-AIO', component_property='figure'),
    Output(component_id='position-graph-SPA', component_property='figure'),
    Output(component_id='position-graph-PA', component_property='figure'),
    Output(component_id='position-graph-FastTrend', component_property='figure'),
    Output(component_id='position-graph-LongShort', component_property='figure'),
    Input(component_id='interval-component-position-graph', component_property='n_intervals'))
def update_position_graph_in_interval(n):
    #
    l_position_figs = []
    for name in L_POSITION_CHECKING_LIST:
        info = D_LIVE_POSITION_FILE_PATH.get(name)
        p_data = info['data']
        p_update = info['update']
        sort_by = info['sort']

        # 数据更新时间
        data_update_dt: datetime = _get_position_update_time(p_update)
        # pivot data
        df = _get_position_data(p_data, sort_by)
        l_columns = df.columns.to_list()
        fig_title = f"{name} _ {str(len(l_columns))} _ {data_update_dt.strftime('%H:%M:%S')}"
        if name == "AIO":
            fig = _gen_position_fig(df, fig_title, width=900)
        else:
            fig = _gen_position_fig(df, fig_title, width=700)
        l_position_figs.append(fig)

        logger.info(f'update position graph, {fig_title}')
    return l_position_figs


# 获取 信号持仓数据
def _get_position_data(p, sort_by='') -> pd.DataFrame:
    df = pd.read_csv(p, names=['ticker', 'trader', 'value'])
    df = df.pivot_table(values='value', index='ticker', columns='trader', aggfunc='sum')
    df = df.fillna(0)  # 补零
    df = df.loc[(df != 0).any(axis=1), :]  # 去除volume 全是0的 ticker
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
def _gen_position_fig(df: pd.DataFrame, fig_title: str, width=700, height=250):
    l_index_sorted_by_value = df.index.to_list()
    l_columns = df.columns.to_list()
    fig = go.Figure()

    l_columns.sort(key=lambda x: str(x).lower().replace('paper', '____'))

    if len(l_columns) == 0:
        return fig

    _max_y = 0
    # _max_y = max([max(df.values), abs(min(df.values))])
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
        if len(y) == 0:
            continue
        _max_y_new = max([abs(_) for _ in y])
        # print(_max_y_new, _max_y, trader)
        if _max_y_new > _max_y:
            _max_y = _max_y_new
    _y_size = round((_max_y * 1.1), -len(str(int(_max_y))) + 2)

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
        yaxis_range=[-_y_size, _y_size],
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
    return fig


# 【2】 AIO信号的持仓ticker变化（合约换月）
@callback(
    Output(component_id='signal-trading-tickers-check', component_property='children'),
    Input('interval-component-trading-tickers-check', 'n_intervals'))
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
            f'信号持仓变化,  更新时间: {_update_time}',
            html.Br(),
            f'新上合约: {", ".join(_new_tickers)}',
            html.Br(),
            f'下线合约: {", ".join(_flatted_tickers)}',
        ]
    else:
        return [
            f'信号持仓变化,  更新时间: {_update_time}',
        ]


# 【3】 AIO信号的持仓ticker变化（合约换月）
# @callback(
#     Output(component_id='bardata-activate-tickers-check', component_property='children'),
#     Input('interval-component-bardata-activate-tickers-check', 'n_intervals'))
# def interval_update_bardata_activate_tickers_check(n):
#     if not L_BARDATA_ACTIVATE_TICKER_INFO_PATH:
#         return ''
#
#     l_all_output = []
#     mdt = datetime.fromtimestamp(os.path.getmtime(L_BARDATA_ACTIVATE_TICKER_INFO_PATH[0]['path']))
#     l_all_output.append(f'DSBar数据检查 (更新时间: {mdt.strftime("%Y-%m-%d %H:%M:%S")})')
#     for info in L_BARDATA_ACTIVATE_TICKER_INFO_PATH:
#         l_output = []
#         name = info['name'].split(' ')[-1]
#         file_path = info['path']
#         if not os.path.isfile(file_path):
#             logger.warning(f'update activate ticker, 找不到此文件,{file_path}')
#             continue
#         with open(file_path) as f:
#             l_lines = f.readlines()
#         for line in l_lines:
#             line = line.strip()
#             if line == '':
#                 continue
#             l_output.append((line.split(',')[2]))
#         if l_output:
#             l_all_output.append(html.Br())
#             l_all_output.append(f"{name}: {','.join(l_output)}")
#
#     # mdt = datetime.fromtimestamp(os.path.getmtime(L_BARDATA_ACTIVATE_TICKER_INFO_PATH[0]['path']))
#     # l_all_output.append(f'DSBar数据检查 UpdateTime: {mdt.strftime("%Y-%m-%d %H:%M:%S")}')
#     return l_all_output
