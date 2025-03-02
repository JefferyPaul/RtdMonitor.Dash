import os
from datetime import datetime, timedelta
import logging
from typing import List

logger = logging.getLogger('DashMonitor_TickerInfo')


from helper.tp_WarningBoard.warning_board import run_warning_board

import pandas as pd
import dash
from dash import html, dcc, callback, Input, Output, dash_table
import plotly.graph_objects as go
import dash_bootstrap_components as dbc


dash.register_page(
    __name__,
    name='3_TickerInfo'
)


# 配置
PATH_NEWEST_GTI_DATA_FILE = r'C:\D\_workspace_A2\AGP.RtdMonitor\Data\NewestGtiData\NewestGtiData.csv'
PATH_GTI_DATA_CHANGED_FILE = r'C:\D\_workspace_A2\AGP.RtdMonitor\Data\CheckWindGtiData\GtiCheckingResult.json'

GTI_DATA_HEADER = [
    "product",
    "commission_on_rate",
    "commission_per_share",
    "point_value",
    "min_move",
    "margin",
    "flat_today_discount",
    "ticker",
    "date",
]


def layout():
    _ = html.Div(
        children=[
            html.H6('Ticker Info'),

            html.Div(
                children=[
                    dash_table.DataTable(
                        id="newest-gti-data",
                        columns=[{"name": _, "id": _} for _ in GTI_DATA_HEADER],
                        fixed_rows={'headers': True},
                        page_action='none',
                        style_table={
                            'height': '2000px', 'overflowY': 'auto'
                        },
                        style_cell={
                            'minWidth': 120, 'maxWidth': 120, 'width': 120
                        },
                        style_as_list_view=True,  #
                        sort_action="native",  # 排序
                        selected_cells='row',
                    ),
                    dcc.Interval(
                        # 定时器，60分钟
                        id='interval-component-newest-gti_table',
                        interval=1000 * 60 * 60,  # in milliseconds
                        n_intervals=0
                    ),
                ],
            )
        ]
    )
    return _


@callback(
    Output(component_id='newest-gti-data', component_property='data'),
    Input(component_id='interval-component-newest-gti_table', component_property='n_intervals'))
def interval_update_newest_gti(n):
    df = pd.read_csv(PATH_NEWEST_GTI_DATA_FILE)
    return df.to_dict('records')

    # with open(PATH_NEWEST_GTI_DATA_FILE) as f:
    #     l_lines = f.readlines()
    # if len(l_lines) < 2:
    #     logger.error(f'Gti数据文件文件为空, {PATH_NEWEST_GTI_DATA_FILE}')
    #     return []
    #
    # l_original_data_in_string = list()
    # header = l_lines[0].split(',')
    # for line in l_lines[1:]:
    #     line = line.strip()
    #     if line == '':
    #         continue
    #     _value = line.split(',')
    #     l_original_data_in_string.append(dict(zip(header, _value)))
    #
    # l_adjusted_data = list()
    # for _data in l_original_data_in_string:
    #     if _data['commission_on_rate'] == '0':
    #         _data['commission_on_rate'] = '-'
    #     else:
    #         _comm = float(_data['commission_on_rate'])
    #     if _data['commission_on_share'] == '0':
    #         _data['commission_on_share'] = '-'





# @callback(
# Output(component_id='newest-gti-data', component_property='data'),
# Input(component_id='interval-component-newest-gti_table', component_property='n_intervals')))
# def interval_update_newest_gti(n):
#     with open(PATH_NEWEST_GTI_DATA_FILE) as f:
#         l_lines = f.readlines()
#     if len(l_lines) < 2:
#         return ''
#
#     header = l_lines[0].strip().split(',')
#     l_data_in_dict: List[dict] = []
#     for line in l_lines[1:]:
#         line = line.strip()
#         if line == '':
#             continue
#         _value = line.split(',')
#         l_data_in_dict.append(dict(zip(header, _value)))
#
#     return dash_table.DataTable(
#         data=l_data_in_dict,
#         columns=[{"name": _, "id": _} for _ in header],
#         fixed_rows={'headers': True},
#         page_action='none',
#         style_table={
#             'height': '2000px', 'overflowY': 'auto'
#         },
#         style_cell={
#             'minWidth': 120, 'maxWidth': 120, 'width': 120
#         },
#         style_as_list_view=True,        #
#         sort_action="native",       # 排序
#     )
