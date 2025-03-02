import os
import pandas as pd
import dash
from dash import html, dcc, callback, Input, Output
from datetime import datetime, timedelta
import logging

logger = logging.getLogger('DashMonitor_Tracking')


from helper.tp_WarningBoard.warning_board import run_warning_board

# from app import app
import plotly.graph_objects as go
import dash_bootstrap_components as dbc


dash.register_page(
    __name__,
    name='2_PnLTracking'
)


# 配置
PATH_TRACKING_DATA_ROOT = r'C:\D\_workspace_A2\AGP.RtdMonitor\Data\TrackingData'
CHECKING_DAYS = 30

D_TRACKING = {
    "AIO": [
        "Tracking.A", "Tracking.Paper.A8_F", "Tracking.Live.DongHang",
        "Tracking.Live.JuLi2", "Tracking.Live.JuLi3", "Tracking.Live.WangRongDao",
        # "Tracking.Live.ShengShi8"
    ],
    "PA": [
        "Tracking.AnthonyPA", "Tracking.Paper.AnthonyPA", "Tracking.Live.Anthony", "Tracking.Live.JiuGeXing",
        # "Tracking.Live.TangYin",
        "Tracking.Live.WanFeng", "Tracking.Live.WenYun2", "Tracking.Live.ShengShi23",
    ],
    "FastTrend": [
        "Tracking.FastTrend", "Tracking.Paper.FastTrend", "Tracking.Live.LiMan2",
    ],
    "PAFF": [
        "Tracking.AnthonyPAFF", "Tracking.Live.AnthonyPAFF",
        "Tracking.Paper.AnthonyPAFF", "Tracking.Paper.AnthonyPAFF_15Twap",
        "Tracking.Paper.AnthonyPAFF_30Twap",
        "Tracking.Paper.AnthonyPAFF_AnthonyInitX",
        "Tracking.Paper.AnthonyPAFF_AnthonyInitX_15Twap",
        "Tracking.Paper.AnthonyPAFF_AnthonyInitX_30Twap",
    ],
    "SPA": [
        "Tracking.SPA", "Tracking.Live.ShengShi8", "Tracking.Paper.S8PA", "Tracking.Paper.S8PA_S8InitX",
    ],
    "LongShort": [
        "Tracking.LongShort", "Tracking.Live.OuLa2",
        "Tracking.Paper.LongShort", "Tracking.Paper.LongShort_Oula2InitX",
    ],
    "Call_1": [
        "Tracking.DLl@CalL28K#Product",
        "Tracking.DLl@Test@CalL28K@30sTWAP@Paper.Call28K_30Twap",
        "Tracking.DLl@CalL58KFF#Product",
        "Tracking.DLl@Test@CalL58KFF@30sTWAP@Paper.Call58KFF_30Twap",
        "Tracking.DLv@CalL28K#Product",
        "Tracking.DLv@Test@CalL28K@30sTWAP@Paper.Call28K_30Twap",
        "Tracking.DLv@CalL58KFF#Product",
        "Tracking.DLv@Test@CalL58KFF@30sTWAP@Paper.Call58KFF_30Twap",
    ],
    "Call_2": [
        "Tracking.DLeb@CalL28KFF#Product",
        "Tracking.DLeb@Test@CalL28KFF@30sTWAP@Paper.Call28KFF_30Twap",
        "Tracking.DLeb@CalL58KFF#Product",
        "Tracking.DLeb@Test@CalL58KFF@30sTWAP@Paper.Call58KFF_30Twap",
        "Tracking.DLpp@CalL58KFF#Product",
        "Tracking.DLpp@Test@CalL58KFF@30sTWAP@Paper.Call58KFF_30Twap",
    ]
}


def layout():
    _ = html.Div(
        children=[
            # 盈亏对比
            # 布局方式 1：
            # html.H5('盈亏对比'),  # 标题
            html.H6('PnL Tracking'),  # 标题

            html.Div(
                children=[
                    html.Div(
                        children=[
                            dcc.Graph(id='tracking-graph-AIO'),  #
                            dcc.Graph(id='tracking-graph-LongShort'),  #
                        ],
                        style={'display': 'flex', 'flex-direction': 'row'}
                    ),
                    html.Div(
                        children=[
                            dcc.Graph(id='tracking-graph-SPA'),  #
                            dcc.Graph(id='tracking-graph-FastTrend'),  #
                        ],
                        style={'display': 'flex', 'flex-direction': 'row'}
                    ),
                    html.Div(
                        children=[
                            dcc.Graph(id='tracking-graph-PA'),  #
                            dcc.Graph(id='tracking-graph-PAFF'),  #
                        ],
                        style={'display': 'flex', 'flex-direction': 'row'}
                    ),
                    html.Div(
                        children=[
                            dcc.Graph(id='tracking-graph-Call-1'),  #
                        ],
                        style={'display': 'flex', 'flex-direction': 'row'}
                    ),
                    html.Div(
                        children=[
                            dcc.Graph(id='tracking-graph-Call-2'),  #
                        ],
                        style={'display': 'flex', 'flex-direction': 'row'}
                    ),
                    dcc.Interval(  # 定时器，10分钟
                        id='interval-component-tracking-graph',
                        interval=1000 * 60 * 20,  # in milliseconds
                        n_intervals=0
                    ),
                ],
                style={'display': 'flex', 'flex-direction': 'column'},
                # style={'display': 'flex', 'flex-direction': 'row'}
            ),
        ],

    # 盈亏对比
    # html.Div(
    #     children=[
    #         "盈亏对比",
    #         dbc.Row(
    #             children=[
    #                 dbc.Col(dcc.Graph(id='tracking-graph-AIO')),
    #                 dbc.Col(dcc.Graph(id='tracking-graph-LongShort')),
    #             ],
    #         ),
    #         dbc.Row(
    #             children=[
    #                 dbc.Col(dcc.Graph(id='tracking-graph-SPA')),
    #                 dbc.Col(dcc.Graph(id='tracking-graph-FastTrend')),
    #             ],
    #         ),
    #         dbc.Row(
    #             children=[
    #                 dbc.Col(dcc.Graph(id='tracking-graph-PA')),
    #                 dbc.Col(dcc.Graph(id='tracking-graph-PAFF')),
    #             ],
    #         ),
    #         dbc.Row(
    #             children=[
    #                 dbc.Col(dcc.Graph(id='tracking-graph-Call-1')),
    #             ],
    #         ),
    #         dbc.Row(
    #             children=[
    #                 dbc.Col(dcc.Graph(id='tracking-graph-Call-2')),
    #             ],
    #         ),
    #         dcc.Interval(
    #             # 定时器，10分钟
    #             id='interval-component-tracking-graph',
    #             interval=1000 * 60 * 10,  # in milliseconds
    #             n_intervals=0
    #         ),
    #     ],
    # ),

        # "盈亏对比",
        # html.Div(
        #     children=[
        #         html.Div(
        #             children=[
        #                 dcc.Graph(id='tracking-graph-AIO'),  #
        #                 dcc.Graph(id='tracking-graph-SPA'),  #
        #                 dcc.Graph(id='tracking-graph-PA'),  #
        #                 dcc.Graph(id='tracking-graph-Call-1'),  #
        #                 dcc.Graph(id='tracking-graph-Call-2'),  #
        #             ],
        #             style={'display': 'flex', 'flex-direction': 'column'}
        #         ),
        #         html.Div(
        #             children=[
        #                 dcc.Graph(id='tracking-graph-LongShort'),  #
        #                 dcc.Graph(id='tracking-graph-FastTrend'),  #
        #                 dcc.Graph(id='tracking-graph-PAFF'),  #
        #             ],
        #             style={'display': 'flex', 'flex-direction': 'column'}
        #         ),
        #         dcc.Interval(  # 定时器，10分钟
        #             id='interval-component-tracking-graph',
        #             interval=1000 * 60 * 20,  # in milliseconds
        #             n_intervals=0
        #         ),
        #     ],
        #     # style={'display': 'flex', 'flex-direction': 'column'},
        #     style={'display': 'flex', 'flex-direction': 'row'}
        # ),
    )
    return _


@callback(
    Output(component_id='tracking-graph-AIO', component_property='figure'),
    Output(component_id='tracking-graph-PA', component_property='figure'),
    Output(component_id='tracking-graph-FastTrend', component_property='figure'),
    Output(component_id='tracking-graph-PAFF', component_property='figure'),
    Output(component_id='tracking-graph-SPA', component_property='figure'),
    Output(component_id='tracking-graph-LongShort', component_property='figure'),
    Output(component_id='tracking-graph-Call-1', component_property='figure'),
    Output(component_id='tracking-graph-Call-2', component_property='figure'),
    Input(component_id='interval-component-tracking-graph', component_property='n_intervals'))
def interval_update_tracking_graph(n):
    l_output = []
    for n, name in enumerate(list(D_TRACKING.keys())):
        keys = D_TRACKING[name]
        # pivot data
        df = _get_tracking_data(keys)
        _data_max_date = max(df.index.to_list())
        l_columns = df.columns.to_list()
        fig_title = f"{name} _ {str(_data_max_date)} _ {str(len(l_columns))}"
        logger.info(f'update tracking graph, {fig_title}')
        if name.find('Call') == 0:
            fig = _gen_tracking_fig(df, fig_title, width=900, height=300)
        else:
            fig = _gen_tracking_fig(df, fig_title)
        l_output.append(fig)
    return l_output


# 获取 ror净值数据
def _get_tracking_data(keys: list) -> pd.DataFrame:
    checking_date = (datetime.today() - timedelta(days=CHECKING_DAYS)).strftime('%Y%m%d')
    # PAFF 新上线，需要特殊处理 2023/11/25
    # if "Tracking.Live.AnthonyPAFF" in keys:
    #     if checking_date < "20231123":
    #         checking_date = "20231123"

    l_all_data = []
    _new_keys = []

    for key in keys:
        # print(key)
        p_file = os.path.join(PATH_TRACKING_DATA_ROOT, key, 'AggregatedPnlSeries.csv')
        if not os.path.isfile(p_file):
            logger.warning(f'get tracking file, 未找到TrackingFile, {key}')
            run_warning_board('未找到TrackingFile')
            continue
        _df = pd.read_csv(p_file, names=['Date', 'RoR'])
        _df = _df[_df.Date >= int(checking_date)]
        _df['Date'] = _df['Date'].apply(lambda _: str(_))
        _name = key.replace("Tracking.", "")
        _df.loc[:, "Name"] = _name
        _new_keys.append(_name)
        l_all_data.append(_df)
    df_all = pd.concat(l_all_data)
    df_all.reset_index(inplace=True)
    df_all_pt = df_all.pivot_table(values='RoR', index='Date', columns='Name', fill_value=0)
    df_all_pt_cumsum = df_all_pt.cumsum()
    df_all_pt_cumsum = df_all_pt_cumsum[_new_keys]
    # print(df_all_pt_cumsum.columns)

    return df_all_pt_cumsum


# 生成 Tracking 净值图
def _gen_tracking_fig(df: pd.DataFrame, fig_title: str, width=750, height=250):
    l_index_sorted_by_value = df.index.to_list()
    l_columns = df.columns.to_list()
    fig = go.Figure()
    # _max_y = 0
    for trader in l_columns:
        y = list(df.loc[:, trader].values)
        # trader_same_width = trader.ljust(30, ' ')       # 统一长度，为了统一图和实例显示的大小
        trader_same_width = trader.ljust(40, ' ')       # 统一长度，为了统一图和实例显示的大小

        fig.add_trace(
            go.Scatter(
                x=l_index_sorted_by_value,
                y=y,
                mode='lines',
                # name=trader,
                name=trader_same_width,
                line=dict(
                    width=1,
                ),
            ))
    #     _max_y_new = max([abs(_) for _ in y])
    #     if _max_y_new > _max_y:
    #         _max_y = _max_y_new
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
        # zeroline=True,
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
        # yaxis_range=[-_y_size, _y_size],
        # 图例位置
        legend=dict(
            # orientation="h",  # 开启水平显示
            # yanchor="bottom",  # y轴顶部  bottom top
            # y=0,
            # xanchor="left",  # x轴靠左
            # 3=0,
            # itemsizing='trace',   # trace 和 constant 两种设置, trace 小图形
            font=dict(size=12),
            font_family="Courier New",  # 等宽字体
        ),
        # showlegend=False   # 隐藏图例元素
    )
    return fig


# for call
# @callback(
#     Output('graph-tracking-7', 'figure'),
#     Output('graph-tracking-8', 'figure'),
#     Input('interval-component-tracking-graph-2', 'n_intervals'))
# def interval_update_tracking_graph_2(n):
#     l_output = []
#     for n, name in enumerate(list(D_TRACKING_2.keys())):
#         keys = D_TRACKING_2[name]
#         # pivot data
#         df = _get_tracking_data(keys)
#         _data_max_date = max(df.index.to_list())
#         l_columns = df.columns.to_list()
#         fig_title = f"{name} _ {str(_data_max_date)} _ {str(len(l_columns))}"
#         logger.info(f'update tracking graph, {fig_title}')
#         fig = _gen_tracking_fig(df, fig_title, width=900, height=300)
#         l_output.append(fig)
#     return l_output
#
