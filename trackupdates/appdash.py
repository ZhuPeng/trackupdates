# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from flask import Flask
from datetime import datetime as dt, timedelta

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


def genlayout(options):
    select_options = []
    for o in options:
        select_options.append({'label': o, 'value': o})
    select_all = [o['label'] for o in select_options]
    itemDropdown = dcc.Dropdown(id='item-dropdown', multi=True, options=select_options, value=select_all)
    selectAllCheckbox = dcc.Checklist(
        id='select-all',
        options=[{'label': 'Select All', 'value': 'Select All'}],
        values=['Select All']
    )
    style = {'width': '75%', 'float': 'right', 'display': 'inline-block', 'line-height': '60px'}

    init = dt.now()-timedelta(days=30)
    layout = html.Div([
        html.H1(children='TrackUpdates Dash'),
        itemDropdown,
        html.Div([
            html.Div([html.P(children='Start Date: ')], style={'width': '8%', 'display': 'inline-block'}),
            html.Div([
                dcc.DatePickerSingle(id='date-picker-single', date=dt(init.year, init.month, init.day))], style={'width': '15%', 'display': 'inline-block'}
            ),
            html.Div([selectAllCheckbox], style=style),
        ]),
        dcc.Graph(id='graph')
    ])
    return layout


def gendash(server, sched):
    app = dash.Dash(__name__, server=server, url_base_pathname='/dash/')
    jobs = {}
    for config in sched.settings.get_all_job_configs():
        jobs[config.get('view', config['name'])] = config['name']

    app.layout = genlayout(jobs.keys())

    @app.callback(Output('item-dropdown', 'value'), [Input('select-all', 'values')])
    def select_all(select):
        print 'select_all: ', select
        if 'Select All' in select:
            return jobs.keys()
        return jobs.keys()[0]

    @app.callback(Output('graph', 'figure'), [Input('item-dropdown', 'value'), Input('date-picker-single', 'date')])
    def callback_item(dropdown_values, start_date):
        if type(dropdown_values) is not list:
            dropdown_values = [dropdown_values]
        print 'callback_item: ', start_date, ', '.join(dropdown_values)

        data, x = [], []
        now = dt.now()
        start = dt.strptime(start_date, "%Y-%m-%d")
        for i in range((now-start).days+1)[::-1]:
            x.append((now - timedelta(days=i)).strftime("%Y-%m-%d"))

        for dropdown_value in dropdown_values:
            count = {}
            for i in x:
                count[i] = 0

            job = jobs[dropdown_value]
            items = sched.jobs[job].store.iter(starttime=start_date)
            for i in items:
                d = i._crawl_time.strftime("%Y-%m-%d")
                if d not in count:
                    continue
                count[d] += 1
            y = []
            for i in x:
                y.append(count[i])
            data.append({'x': x, 'y': y, 'type': 'line', 'name': dropdown_value})
        return {
            'data': data,
            'layout': {'title': '每天抓取数量'}
        }
    return app

if __name__ == '__main__':
    server = Flask(__name__)
    app = gendash(server)
    app.run_server(debug=True)
