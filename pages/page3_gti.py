import os
import logging
import json
from typing import List


import pandas as pd
import dash
from dash import html, dcc, callback, Input, Output, dash_table
import plotly.graph_objects as go
import dash_bootstrap_components as dbc


dash.register_page(
    __name__,
    name='TickerInfo'
)


# 配置
PATH_NEWEST_GTI_DATA_FILE = r'C:\D\_workspace_A2\AGP.RtdMonitor\Data\NewestGtiData\NewestGtiData.csv'
PATH_GTI_DATA_CHANGED_FILE = r'C:\D\_workspace_A2\AGP.RtdMonitor\Data\CheckWindGtiData\GtiCheckingResult.json'

GTI_DATA_HEADER = [
    "product",
    "commission_on_rate",
    "commission_per_share",
    "flat_today_discount",
    "margin",
    "point_value",
    "min_move",
    "ticker",
    "date",
]


def layout():
    _ = html.Div(
        children=[
            html.H5('( 20:30 更新 )'),
            html.H5('最新变化:'),
            dash_table.DataTable(
                id="changed-gti-data",
                columns=[{"name": _, "id": _} for _ in GTI_DATA_HEADER],
                fixed_rows={
                    'headers': True
                },
                style_cell={
                    'minWidth': 100, 'maxWidth': 200, 'width': 150
                },
                style_as_list_view=True,  #
                sort_action="native",  # 排序
            ),

            html.H5('有特殊设定的品种:'),
            dash_table.DataTable(
                id="nonstandard-gti-data",
                columns=[{"name": _, "id": _} for _ in GTI_DATA_HEADER],
                fixed_rows={
                    'headers': True
                },
                style_cell={
                    'minWidth': 100, 'maxWidth': 200, 'width': 150
                },
                style_as_list_view=True,  #
                sort_action="native",  # 排序
            ),

            html.H5('Ticker Info'),
            dash_table.DataTable(
                id="newest-gti-data",
                columns=[{"name": _, "id": _} for _ in GTI_DATA_HEADER],
                fixed_rows={
                    'headers': True
                },
                # page_action='none',
                # style_table={
                #     'height': '2000px', 'overflowY': 'auto'
                # },
                style_cell={
                    'minWidth': 100, 'maxWidth': 200, 'width': 150
                },
                style_as_list_view=True,  #
                sort_action="native",  # 排序
                # selected_cells='row',
            ),
            dcc.Interval(
                # 定时器，60分钟
                id='interval-component',
                interval=1000 * 60 * 60,  # in milliseconds
                n_intervals=0
            ),
        ],
    )
    return _


@callback(
    Output(component_id='newest-gti-data', component_property='data'),
    Input(component_id='interval-component', component_property='n_intervals'))
def interval_update_newest_gti(n):
    df = pd.read_csv(PATH_NEWEST_GTI_DATA_FILE)
    return df.to_dict('records')


@callback(
    Output(component_id='changed-gti-data', component_property='data'),
    Output(component_id='nonstandard-gti-data', component_property='data'),
    Input(component_id='interval-component', component_property='n_intervals'))
def interval_update_checked_gti(n):
    d_data = json.loads(open(PATH_GTI_DATA_CHANGED_FILE).read(), )
    l_data_changed = d_data['Changed']
    l_data_nonstandard = d_data['Nonstandard']

    # 特殊设定
    # if l_data_nonstandard:
    #     l_data_nonstandard = [
    #         __
    #         for _ in l_data_nonstandard
    #         for __ in _
    #     ]
    l_data_changed_mix = list()
    if l_data_changed:
        for _data in l_data_changed:
            _new_data = _data[0]
            _standard_data = _data[1]
            for _key in [
                "point_value", "min_move", "commission_on_rate", "commission_per_share",
                "flat_today_discount", "margin"
            ]:
                _new_value = float(_new_data[_key])
                _old_value = float(_standard_data[_key])
                if _new_value != _old_value:
                    _new_data[_key] = f'{str(_new_value)}  [{str(_old_value)}]'
            l_data_changed_mix.append(_new_data)

    l_data_nonstandard_mix = list()
    if l_data_nonstandard:
        for _data in l_data_nonstandard:
            _new_data = _data[0]
            _standard_data = _data[1]
            for _key in [
                "point_value", "min_move", "commission_on_rate", "commission_per_share",
                "flat_today_discount", "margin"
            ]:
                _new_value = float(_new_data[_key])
                _old_value = float(_standard_data[_key])
                if _new_value != _old_value:
                    _new_data[_key] = f'{str(_new_value)}  [{str(_old_value)}]'
            l_data_nonstandard_mix.append(_new_data)

    return l_data_changed_mix, l_data_nonstandard_mix



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
