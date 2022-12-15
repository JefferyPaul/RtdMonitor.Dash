from datetime import datetime
import os
from typing import Dict, List

import pandas as pd
import numpy as np
import dash
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go


D_FILE_PATH = {
    "signal": {
        "data": r'D:\_workspace\alphasys\AlphaSysGuardingPlatform'
                r'\TradingServer\AGP.RtdMonitor\Data\SignalData_CnCom.Trend.20220616\signals.csv',
        "sort": "JuLi2"
    },
}

# DATA_FILE = r'D:\_workspace\alphasys\AlphaSysGuardingPlatform\TradingServer' \
#             r'\_DailyCheck.4.AGP.OMS.LivePositionViewer\OMS.LivePosition.DataHandler' \
#             r'\_Output_3_PositionPInitX\AIO\data.csv'
# UPDATE_TIME_FILE = r'D:\_workspace\alphasys\AlphaSysGuardingPlatform\TradingServer' \
#             r'\_DailyCheck.4.AGP.OMS.LivePositionViewer\OMS.LivePosition.DataHandler' \
#             r'\_Output_3_PositionPInitX\AIO\_update.csv'
# SORT_BY_TRADER = 'ShengShi23'
# TITLE = 'AIO'
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(
    __name__,
    # external_stylesheets=external_stylesheets
)
app.layout = html.Div(
    html.Div([
        html.H4('Testing Dash LiveSignal'),
        dcc.Graph(id='graph-Signal'),
        dcc.Interval(
            id='interval-component',
            interval=20*1000,    # in milliseconds
            n_intervals=0
        )
    ])
)


# Multiple components can update everytime interval gets fired.
@app.callback(
    Output('graph-Signal', 'figure'),
    Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    l_fig = []
    for name, info in D_FILE_PATH.items():
        p_data = info['data']
        # 数据更新时间
        data_update_dt: datetime = datetime.fromtimestamp(os.path.getmtime(p_data))
        # groupby data,    ticker, value
        df = get_data(p_data)
        fig_title = f"{name} _ {data_update_dt.strftime('%H:%M:%S')}"
        fig = gen_fig(df, fig_title)
        print(fig_title)
        l_fig.append(fig)

    # fig.update_traces(
    #     line=dict(width=1))
    return l_fig[0]


def get_data(p) -> pd.DataFrame:
    df = pd.read_csv(p, names=['dt', 'ticker', 'target'])
    df = df.groupby('ticker')

    # df.sort_values(['dt', 'ticker'], inplace=True)
    return df


def gen_fig(df: pd.DataFrame, fig_title: str):
    # l_index_sorted_by_value = df.index.to_list()
    # l_columns = df.columns.to_list()
    d_ticker_df: Dict[str, pd.DataFrame] = {}
    for ticker, data in df:
        d_ticker_df[ticker] = data

    fig = go.Figure()
    for ticker in sorted(list(d_ticker_df.keys()), key=lambda x: x.lower()):
        data = d_ticker_df[ticker]
        data.sort_values('dt', ascending=True, inplace=True)
        _x = [datetime.strptime(_dt, '%Y%m%d %H%M%S') for _dt in data.loc[:, 'dt'].to_list()]
        _y = data.loc[:, 'target'].to_list()
        fig.add_trace(
            go.Scatter(
                x=_x,
                y=_y,
                mode='lines',
                name=ticker,
                line=dict(
                    width=0.5
                ),
                line_shape='hv'
            )
        )

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
            size=13
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
        height=800,
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


if __name__ == '__main__':
    app.run_server(host='192.168.1.72', debug=True)
