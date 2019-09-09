import dash
import dash_table
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import pickle
# from spotify_fetching import *
import numpy as np
# from Playlist import playlist
from Table import table
app = dash.Dash(__name__)

# table = pickle.load(open('sample.p', 'rb'))
display_cols = ['name', 'artist_name', 'genres', 'release_date', 'duration']
table.playlist_descriptions
df = table.data[display_cols]


app.layout = html.Div([
    dash_table.DataTable(
        id='datatable-interactivity',
        columns=[
            {"name": i, "id": i, "deletable": True} for i in df.columns
        ],
        data=df.to_dict('records'),
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        row_selectable="multi",
        row_deletable=True,
        selected_rows=[],
        page_action="native",
        page_current= 0,
        page_size= 10,
        style_cell={'textAlign': 'right'},
        style_data_conditional=[{'if': {'column_id': 'name'},
                                 'textAlign': 'left'},
                                {'if': {'column_id': 'artist_name'},
                                 'textAlign': 'left'},
                                {'if': {'column_id': 'genres'},
                                 'textAlign': 'left'}]
    ),
    html.Div(id='datatable-interactivity-container')
])


# @app.callback(
#     Output('datatable-interactivity', 'style_data_conditional'),
#     [Input('datatable-interactivity', 'selected_rows')]
# )
# def update_styles(selected_columns):
#     return [{
#         'if': { 'column_id': i },
#         'background_color': '#D2F3FF'
#     } for i in selected_rows]



if __name__ == '__main__':
    app.run_server(debug=True)
