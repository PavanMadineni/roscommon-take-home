import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import plotly.express as px
import argparse
import os

class DashApp:
    def __init__(self,data_path):
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.df = pd.read_csv(data_path)
        self.PAGE_SIZE = 100
        self.setup_layout()
        
    def setup_layout(self):
        
        # define the layout of the app
        self.app.layout = html.Div(children=[
            dcc.Tabs(id='tabs', value='tab-1', children=[
                dcc.Tab(label='Table', value='tab-1', children=[
                    html.H3(children='UK Power Demand Data', style={'text-align': 'center'}), 
                    html.Div([
                        # create a table component
                        dash_table.DataTable(
                            id='table',
                            columns=[{'name': i, 'id': i} for i in self.df.columns],
                            data=self.df.head(self.PAGE_SIZE).to_dict('records'),
                            page_size=self.PAGE_SIZE,
                            style_table={'overflowX': 'scroll', 'overflowY': 'scroll',
                                        'height': '700px'}
                        )
                    ]),

                    # add pagination controls
                    dbc.Pagination(
                        id='table-pagination',
                        size='md',
                        max_value=(len(self.df) // self.PAGE_SIZE) + 1 if len(self.df) % self.PAGE_SIZE != 0 else len(self.df) // self.PAGE_SIZE,
                        fully_expanded=False,
                        first_last=True,
                        previous_next=True,
                        style={'justify-content': 'center', "margin-top": "10px"}
                    )
                ]),

                dcc.Tab(label='Chart', value='tab-2', children=[
                    dbc.Container([
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(
                                    id="chart_graph",
                                    figure={},
                                ),

                                # add pagination controls
                                dbc.Pagination(
                                    id='chart-pagination',
                                    size='md',
                                    max_value=(len(self.df) // self.PAGE_SIZE) + 1 if len(self.df) % self.PAGE_SIZE != 0 else len(self.df) // self.PAGE_SIZE,
                                    fully_expanded=False,
                                    first_last=True,
                                    previous_next=True,
                                    style={'justify-content': 'center', "margin-top": "25px", "color": "#800000"}
                                )
                            ], width=8),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader("Chart Options"),
                                    dbc.CardHeader("Select chart type, group column (abscissa x-axis) and series (ordinate y-axis)", style={"fontSize": "12px"}),
                                    dbc.CardBody([
                                        html.Label('Chart Type'),
                                        dcc.Dropdown(
                                           id="chart_type",
                                           options=[{"label": "Line", "value": "line"},
                                                   {"label": "Bar", "value": "bar"}],
                                           value="line",
                                           style={"width": "100%"}
                                       ),
                                       html.Br(),

                                       html.Label('Group Column'),
                                        dcc.Dropdown(
                                            id='group_column_dropdown',
                                            options=[{'label': col, 'value': col} for col in self.df.columns],
                                            value=self.df.columns[0],
                                            style={"width": "100%"}
                                        ),
                                        html.Br(),

                                        html.Label('Series'),
                                        dcc.Checklist(
                                            id="series_checklist",
                                            options=[{'label': col.lower(), 'value': col} for col in self.df.columns],
                                            value=[],
                                            labelStyle={'margin-right': '10px'},
                                            inputStyle={'margin-right': '16px'},
                                            style={'margin-top': '8px'}
                                        ),

                                        html.Br(),
                                        html.Button(
                                            id="add_view",
                                            n_clicks=0,
                                            children="Add View",
                                            style={
                                                "margin": "auto",
                                                "display": "block",
                                                "background-color": "#800000",
                                                "color": "white",
                                                "font-size": "16px",
                                                "padding": "7px",
                                                "textAlign": "center"
                                            }
                                        )
                                    ])
                                ], style={"width": "65%", "margin-top": "20px", "margin-left": "20px"}) 
                            ], width=4)
                        ])
                    ], fluid=True,),

                ])

            ])
        ])
        
    def setup_callbacks(self):
        @self.app.callback(
            Output('table', 'data'),
            [Input('table-pagination', 'active_page')]
        )
        def update_table(active_page):
            if active_page is None:
                active_page = 1
            return self.df.iloc[(active_page - 1) * self.PAGE_SIZE:active_page * self.PAGE_SIZE].to_dict('records')

        @self.app.callback(
            Output(component_id='chart_graph', component_property='figure'),
            [Input(component_id='add_view', component_property='n_clicks')],
            [State(component_id='chart_type', component_property='value'),
             State(component_id='group_column_dropdown', component_property='value'),
             State(component_id='series_checklist', component_property='value'),
             Input(component_id='chart-pagination', component_property='active_page')]
        )
        def update_chart(n_clicks, chart_type, group_column, series_columns, active_page):
            if active_page is None:
                active_page = 1

            active_page = int(active_page)
            start_index = (active_page - 1) * self.PAGE_SIZE
            end_index = active_page * self.PAGE_SIZE
            data = self.df.iloc[start_index:end_index]

            filtered_df = data.loc[:, [group_column] + series_columns]
            grouped_df = filtered_df.groupby([group_column]).sum().reset_index()

            traces = []
            for col in series_columns:
                if chart_type == 'line':
                    trace = go.Scatter(x=grouped_df[group_column], y=grouped_df[col], name=col,
                                       mode="lines+markers", line=dict(width=2), marker=dict(size=8))
                else:
                    trace = go.Bar(x=grouped_df[group_column], y=grouped_df[col], name=col)
                traces.append(trace)

            fig = go.Figure(data=traces)

            fig.update_layout(
                title=f"{', '.join(series_columns)} by {group_column}",
                xaxis=dict(title=group_column, tickmode="linear"),
                yaxis=dict(title=', '.join(series_columns)),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2),
                margin=dict(l=40, r=40, t=60, b=40),
                plot_bgcolor="#f2f2f2",
                paper_bgcolor="#ffffff",
                height=750,
                width=1000
            )

            return fig

    def run_server(self):
        self.app.run_server(debug=True, host='127.0.0.1', port=8050, use_reloader=False)

# Create an ArgumentParser object
parser = argparse.ArgumentParser(description='Dash Application')

# Add an argument for the data path
parser.add_argument('--data_path', type=str, default='../data/demanddata_2022.csv', help='Path to the data files')
        
def main():
    # Parse the command-line arguments
    args = parser.parse_args()

    # Access the data path from the parsed arguments
    data_path = args.data_path
    myApp = DashApp(data_path)
    myApp.setup_layout()
    myApp.setup_callbacks()
    myApp.run_server()

if __name__ == '__main__':
    main()
