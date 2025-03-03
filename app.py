import os
import sys

import dash
from dash import Dash, dcc, html
# from helper.mylogger import setup_logging
import dash_bootstrap_components as dbc


# setup_logging()

# 将项目根目录添加到 PYTHONPATH
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)


app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP]     # 使用 dbc bootstrap主题
)


app.layout = html.Div([
    # html.Div([
    #     html.Div(
    #         dcc.Link(
    #             # f"{page['name']}",
    #             html.Button(f"{page['name']}"),
    #             href=page["relative_path"]
    #         )
    #     ) for page in dash.page_registry.values()
    # ]),
    # dbc.Row([
    #     dcc.Link(
    #         dbc.Button(str(page['name']), color='info'),
    #         href=page["relative_path"]
    #     )
    #     for page in dash.page_registry.values()
    # ]),
    # dbc.Nav(
    #     [
    #         dbc.NavItem(dbc.NavLink(page['name'], href=page['relative_path']))
    #         for page in dash.page_registry.values()
    #     ],
    #     pills=True, fill=True
    # ),
    # dbc.NavbarSimple(
    #     children=[
    #         dbc.NavItem(dbc.NavLink(page['name'], href=page['relative_path']))
    #         for page in dash.page_registry.values()
    #     ],
    #     color='primary',
    #     dark=True,
    #     links_left=True,
    # ),
    dbc.NavbarSimple(
        children=[
            dbc.NavLink(
                dbc.Button(
                    page['name'], color='primary', outline=True
                ),
                href=page['relative_path']
            )
            # for _page_name in ['LivePosition', 'PnLTracking', 'TickerInfo']
            for page in dash.page_registry.values()
        ],
        # color='primary',
        dark=True,
        links_left=True,
        # brand='Pages:',
        # color="dark",
    ),
    dash.page_container,
])


if __name__ == '__main__':
    # from pages.page6_holdingPositionValue import init_callbacks
    # init_callbacks(app)
    app.run_server(host='0.0.0.0', port='8050', debug=True)
