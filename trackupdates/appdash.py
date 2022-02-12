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
        value=['Select All']
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
        dcc.Graph(id='crawl-count-graph'),
        dcc.Graph(id='top-count-words-graph'),
    ])
    return layout


def is_filter_word(w):
    import nltk
    from nltk.corpus import stopwords
    nltk.download('stopwords')
    nltk.download('punkt')
    STOPWORDS = stopwords.words('english')
    if w not in STOPWORDS and w.isalpha():
        return True
    return False


def gendash(server, sched):
    app = dash.Dash(__name__, server=server, url_base_pathname='/dash/')
    jobs = {}
    for config in sched.settings.get_all_job_configs():
        jobs[config.get('view', config['name'])] = config['name']

    app.layout = genlayout(jobs.keys())

    @app.callback(Output('item-dropdown', 'value'), [Input('select-all', 'value')])
    def select_all(select):
        print 'select_all: ', select
        if 'Select All' in select:
            return jobs.keys()
        return jobs.keys()[0]

    @app.callback(Output('crawl-count-graph', 'figure'), [Input('item-dropdown', 'value'), Input('date-picker-single', 'date')])
    def callback_crawl_count(dropdown_values, start_date):
        x, dbs = db_select(dropdown_values, start_date)
        data = []
        total = 0
        for k, items in dbs.items():
            count, y = {}, []
            for i in items:
                day = i._crawl_time.strftime("%Y-%m-%d")
                count[day] = count.get(day, 0) + 1
            for j in x:
                y.append(count.get(j, 0))
            total += sum(y)
            data.append({'x': x, 'y': y, 'type': 'line', 'name': k})
        return {'data': data, 'layout': {'title': 'Crawl Count [Total: %d]' % total}}

    @app.callback(Output('top-count-words-graph', 'figure'), [Input('item-dropdown', 'value'), Input('date-picker-single', 'date')])
    def callback_top_words(dropdown_values, start_date):
        from nltk.tokenize import word_tokenize
        x, dbs = db_select(dropdown_values, start_date)
        data, top_words, day_words_cnt = [], {}, {}
        for i in x:
            day_words_cnt[i] = {}
        for k, items in dbs.items():
            for i in items:
                if not hasattr(i, 'title'):
                    continue
                day = i._crawl_time.strftime("%Y-%m-%d")
                for w in word_tokenize(i.title):
                    w = w.lower()
                    top_words[w] = top_words.get(w, 0), + 1
                    day_words_cnt[day][w] = day_words_cnt[day].get(w, 0) + 1
        words = [w[0] for w in sorted(top_words.items(), key=lambda d: d[1], reverse=True)[:100] if is_filter_word(w[0])]
        for w in words:
            y = []
            for i in x:
                y.append(day_words_cnt[i].get(w, 0))
            data.append({'x': x, 'y': y, 'type': 'line', 'name': w})
        return {'data': data, 'layout': {'title': 'Top Count Words'}}

    def db_select(dropdown_values, start_date):
        if type(dropdown_values) is not list:
            dropdown_values = [dropdown_values]
        print 'callback: ', start_date, ', '.join(dropdown_values)

        data, x = {}, []
        now = dt.now()
        start = dt.strptime(start_date, "%Y-%m-%d")
        for i in range((now-start).days+1)[::-1]:
            x.append((now - timedelta(days=i)).strftime("%Y-%m-%d"))

        for dropdown_value in dropdown_values:
            job = jobs[dropdown_value]
            items = sched.jobs[job].store.iter(starttime=start_date, num=-1)
            data[dropdown_value] = items
        return x, data
    return app

if __name__ == '__main__':
    server = Flask(__name__)
    app = gendash(server)
    app.run_server(debug=True)
