import os
import pandas as pd
import dash
from dash import html, dcc, callback, Input, Output
from datetime import datetime, timedelta
# import logging
#
# logger = logging.getLogger('DashMonitor_Tracking')


from helper.tp_WarningBoard.warning_board import run_warning_board

# from app import app
import plotly.graph_objects as go
import dash_bootstrap_components as dbc


dash.register_page(
    __name__,
    name='PnLTracking'
)


# 配置
PATH_TRACKING_DATA_ROOT = r'C:\D\_workspace_A2\AGP.RtdMonitor\Data\TrackingData'
CHECKING_DAYS = 60


D_TRACKING = {
    "PA1": [
        "Tracking.PA1", "Tracking.Paper.PA1", "Tracking.Live.JiuGeXing",
        "Tracking.Live.WanFeng", "Tracking.Live.WenYun2", "Tracking.Live.WenYun4","Tracking.Live.ShengShi23",
    ],
    #"PA2": [
    #    "Tracking.PA2", 
    #    # "Tracking.Paper.PA2", # "Tracking.Live.Anthony"
    #],
    "SPA": [
        "Tracking.SPA", "Tracking.Live.ShengShi8", 
        "Tracking.Live.DongHang", "Tracking.Live.WangRongDao", "Tracking.Live.WenYun5",
        "Tracking.Paper.SPA", 
        "Tracking.Paper.SPA_SS8InitX", 
        # "Tracking.Paper.SPA_LiMan2InitX",
    ],
    "SPA_AG": [
        "Tracking.SPA_AG",
        "Tracking.Live.HuCheJinQu1",
        "Tracking.Paper.SPA_AG",
    ],
    
    # 113
    "113_SQlu": [
        "Tracking.SQlu_113",
        #"Tracking.AIO@Test@SQlu_113@Paper.SQlu_113",
        #"Tracking.AIO@Test@SQlu_113@60sTWAP@Paper.SQlu_113",
    ],
    "TT": [
        "Tracking.PA2_TT",
        #"Tracking.Paper.PA2_TT"
    ],
    

    # call_stable
    "DLeb_CalL28K": [
        "Tracking.DLeb@CalL28K#Product",
        "Tracking.DLeb@Test@CalL28K@Paper.Call28K",
        #"Tracking.DLeb@Test@CalL28K@60sTWAP__2@Paper.Call28K_60sTWAP",
    ],
    "DLeb_CalL58K": [
        "Tracking.DLeb@CalL58K#Product",
        "Tracking.DLeb@Test@CalL58K_2@Paper.Call58K",
        #"Tracking.DLeb@Test@CalL58K_2@60sTWAP__2@Paper.Call28K_60sTWAP",
    ],
    # "DLeb_CalL28KFF": [
        # "Tracking.DLeb@CalL28KFF#Product",
        # "Tracking.DLeb@Test@CalL28KFF_2@Paper.Call28KFF",
        # "Tracking.DLeb@Test@CalL28KFF_2@60sTWAP__2@Paper.Call28K_60sTWAP",
    # ],
    "DLpg_CalL28K": [
        "Tracking.DLpg@CalL28K#Product",
        "Tracking.DLpg@Test@CalL28K@Paper.Call28K",
        #"Tracking.DLpg@Test@CalL28K@60sTWAP__2@Paper.Call28K_60sTWAP",
    ],
    "DLm_CalL28K": [
        "Tracking.DLm@CalL28K#Product",
        "Tracking.DLm@Test@CalL28K@Paper.Call28K",
        #"Tracking.DLm@Test@CalL28K@60sTWAP__2@Paper.Call28K_60sTWAP",
    ],
    "ZZRM_CalL28K": [
        "Tracking.ZZRM@CalL28K#Product",
        "Tracking.ZZRM@Test@CalL28K@Paper.Call28K",
        #"Tracking.ZZRM@Test@CalL28K@60sTWAP__2@Paper.Call28K_60sTWAP",
    ],
    "SQal_CalL28K": [
        "Tracking.SQal@CalL28K#Product",
        "Tracking.SQal@Test@CalL28K@Paper.Call28K",
        #"Tracking.SQal@Test@CalL28K@60sTWAP__2@Paper.Call28K_60sTWAP",
    ],
    "SQal_CalL58K": [
        "Tracking.SQal@CalL58K#Product",
        "Tracking.SQal@Test@CalL58K_2@Paper.Call58K",
        #"Tracking.SQal@Test@CalL58K_2@60sTWAP__2@Paper.Call28K_60sTWAP",
    ],
    "DLeg_CalL28K": [
        "Tracking.DLeg@CalL28K#Product",
        "Tracking.DLeg@Test@CalL28K@Paper.Call28K",
        #"Tracking.DLeg@Test@CalL28K@60sTWAP__2@Paper.Call28K_60sTWAP",
    ],
    # "DLl_CalL28K": [
        # "Tracking.DLl@CalL28K#Product",
        # "Tracking.DLl@Test@CalL28K@Paper.Call28K",
        # "Tracking.DLl@Test@CalL28K@60sTWAP__2@Paper.Call28K_60sTWAP",
    # ],
    # "DLpp_CalL28K": [
        # "Tracking.DLpp@CalL28K#Product",
        # "Tracking.DLpp@Test@CalL28K@Paper.Call28K",
        # "Tracking.DLpp@Test@CalL28K@60sTWAP__2@Paper.Call28K_60sTWAP",
    # ],
    "DLv_CalL28K": [
        "Tracking.DLv@CalL28K#Product",
        "Tracking.DLv@Test@CalL28K@Paper.Call28K",
        #"Tracking.DLv@Test@CalL28K@60sTWAP__2@Paper.Call28K_60sTWAP",
    ],
    "SQfu_CalL28K": [
        "Tracking.SQfu@CalL28K#Product",
        "Tracking.SQfu@Test@CalL28K@Paper.Call28K",
        #"Tracking.SQfu@Test@CalL28K@60sTWAP__2@Paper.Call28K_60sTWAP",
    ],
    "SQni_CalL28K": [
        "Tracking.SQni@CalL28K#Product",
        "Tracking.SQni@Test@CalL28K@Paper.Call28K",
        #"Tracking.SQni@Test@CalL28K@60sTWAP__2@Paper.Call28K_60sTWAP",
    ],
    "SQzn_CalL28K": [
        "Tracking.SQzn@CalL28K#Product",
        "Tracking.SQzn@Test@CalL28K@Paper.Call28K",
        #"Tracking.SQzn@Test@CalL28K@60sTWAP__2@Paper.Call28K_60sTWAP",
    ],
}


def layout():
    _ = html.Div(
        children=[
            # 盈亏对比
            # 布局方式 1：
            # html.H5('盈亏对比'),  # 标题
            html.H6('PnL Tracking  ( T+1 08:30 更新 )'),  # 标题

            html.Div(
                children=[
                    html.Div(
                        children=[
                            dcc.Graph(id='tracking-graph-SPA'),  #
                            dcc.Graph(id='tracking-graph-PA1'),  #
                        ],
                        style={'display': 'flex', 'flex-direction': 'row'}
                    ),
                    html.Div(
                        children=[            
                            dcc.Graph(id='tracking-graph-SPA_AG'),  #   
                            # dcc.Graph(id='tracking-graph-SPA'),  #
                            # dcc.Graph(id='tracking-graph-FastTrend'),  #
                        ],
                        style={'display': 'flex', 'flex-direction': 'row'}
                    ),

                    # ===========  Call ===========
                    html.H6('Call'),  # 标题
                    html.Div(
                        children=[
                         
                            # dcc.Graph(id='tracking-graph-PA2'),  #    
                            dcc.Graph(id='tracking-graph-113_SQlu'),  #
                            dcc.Graph(id='tracking-graph-TT'),  #
                        ],
                        style={'display': 'flex', 'flex-direction': 'row'}
                    ),
                    html.Div(
                        children=[
                            dcc.Graph(id='tracking-graph-DLeb_CalL28K'),  #
                            dcc.Graph(id='tracking-graph-DLeb_CalL58K'),  #
                        ],
                        style={'display': 'flex', 'flex-direction': 'row'}
                    ),
                    html.Div(
                        children=[
                            # dcc.Graph(id='tracking-graph-DLeb_CalL28KFF'),  #
                            dcc.Graph(id='tracking-graph-DLpg_CalL28K'),  #
                        ],
                        style={'display': 'flex', 'flex-direction': 'row'}
                    ),
                    html.Div(
                        children=[
                            dcc.Graph(id='tracking-graph-DLm_CalL28K'),  #
                            dcc.Graph(id='tracking-graph-ZZRM_CalL28K'),  #
                        ],
                        style={'display': 'flex', 'flex-direction': 'row'}
                    ),
                    html.Div(
                        children=[
                            dcc.Graph(id='tracking-graph-SQal_CalL28K'),  #
                            dcc.Graph(id='tracking-graph-SQal_CalL58K'),  #
                        ],
                        style={'display': 'flex', 'flex-direction': 'row'}
                    ),
                    html.Div(
                        children=[
                            dcc.Graph(id='tracking-graph-DLeg_CalL28K'),  #
                            # dcc.Graph(id='tracking-graph-DLl_CalL28K'),  #
                        ],
                        style={'display': 'flex', 'flex-direction': 'row'}
                    ),
                    html.Div(
                        children=[
                            # dcc.Graph(id='tracking-graph-DLpp_CalL28K'),  #
                            dcc.Graph(id='tracking-graph-DLv_CalL28K'),  #
                        ],
                        style={'display': 'flex', 'flex-direction': 'row'}
                    ),
                    html.Div(
                        children=[
                            dcc.Graph(id='tracking-graph-SQfu_CalL28K'),  #
                            dcc.Graph(id='tracking-graph-SQni_CalL28K'),  #
                        ],
                        style={'display': 'flex', 'flex-direction': 'row'}
                    ),
                    html.Div(
                        children=[
                            dcc.Graph(id='tracking-graph-SQzn_CalL28K'),  #
                        ],
                        style={'display': 'flex', 'flex-direction': 'row'}
                    ),

                    # # 定时器，10分钟
                    dcc.Interval(
                        id='interval-component-tracking-graph',
                        interval=1000 * 60 * 20,  # in milliseconds
                        n_intervals=0
                    ),
                ],
                style={'display': 'flex', 'flex-direction': 'column'},
                # style={'display': 'flex', 'flex-direction': 'row'}
            ),
        ],

    )
    return _


@callback(
    # Output(component_id='tracking-graph-AIO', component_property='figure'),
    Output(component_id='tracking-graph-PA1', component_property='figure'),
    #Output(component_id='tracking-graph-PA2', component_property='figure'),
    # Output(component_id='tracking-graph-FastTrend', component_property='figure'),
    # Output(component_id='tracking-graph-PAFF', component_property='figure'),
    Output(component_id='tracking-graph-SPA', component_property='figure'),
    Output(component_id='tracking-graph-SPA_AG', component_property='figure'),
    # Output(component_id='tracking-graph-LongShort', component_property='figure'),
    # Output(component_id='tracking-graph-113Sec', component_property='figure'),
    Output(component_id='tracking-graph-113_SQlu', component_property='figure'),
    Output(component_id='tracking-graph-TT', component_property='figure'),
    Output(component_id='tracking-graph-DLeb_CalL28K', component_property='figure'),
    Output(component_id='tracking-graph-DLeb_CalL58K', component_property='figure'),
    # Output(component_id='tracking-graph-DLeb_CalL28KFF', component_property='figure'),
    Output(component_id='tracking-graph-DLpg_CalL28K', component_property='figure'),
    Output(component_id='tracking-graph-DLm_CalL28K', component_property='figure'),
    Output(component_id='tracking-graph-ZZRM_CalL28K', component_property='figure'),
    Output(component_id='tracking-graph-SQal_CalL28K', component_property='figure'),
    Output(component_id='tracking-graph-SQal_CalL58K', component_property='figure'),
    Output(component_id='tracking-graph-DLeg_CalL28K', component_property='figure'),
    # Output(component_id='tracking-graph-DLl_CalL28K', component_property='figure'),
    # Output(component_id='tracking-graph-DLpp_CalL28K', component_property='figure'),
    Output(component_id='tracking-graph-DLv_CalL28K', component_property='figure'),
    Output(component_id='tracking-graph-SQfu_CalL28K', component_property='figure'),
    Output(component_id='tracking-graph-SQni_CalL28K', component_property='figure'),
    Output(component_id='tracking-graph-SQzn_CalL28K', component_property='figure'),
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
        print(f'update tracking graph, {fig_title}')
        if name.find('Call') == 0:
            # fig = _gen_tracking_fig(df, fig_title, width=900, height=300)
            fig = _gen_tracking_fig(df, fig_title)
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
            print(f'get tracking file, 未找到TrackingFile, {key}')
            run_warning_board('未找到TrackingFile')
            continue
        _df = pd.read_csv(p_file, names=['Date', 'RoR'])
        _df = _df[_df.Date >= int(checking_date)]
        _df['Date'] = _df['Date'].apply(lambda _: str(_))
        _name = key.replace("Tracking.", "")
        
        #_df.loc[:, "Name"] = _name
        #"""
        try:
            _df.loc[:, "Name"] = _name
        except:
            print('not find file,  ' + p_file)
            continue
        #"""
        
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
        # tickfont=dict(
        #     size=12
        # ),
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

