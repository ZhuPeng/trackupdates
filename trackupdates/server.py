# -*- coding: utf-8 -*-
import yaml
import os
import markdown2
from . import appdash
import logging
from signal import signal, SIGINT, SIGTERM
from flask import Flask, request, jsonify, abort, send_from_directory
logger = logging.getLogger(__file__)
dir_path = os.path.dirname(os.path.realpath(__file__))


class Server:
    def __init__(self, sched):
        server = Flask(__name__, static_url_path='')
        server.logger.setLevel(logging.ERROR)
        self.sched = sched
        self.dash = appdash.gendash(server, sched)
        self.init_route()

    def init_route(self):
        app = self.dash.server
        settings = self.sched.settings

        @app.route('/')
        def index():
            return send_from_directory(os.path.join(dir_path, '../web/dist'), 'index.html')

        @app.route('/dash/')
        def dash():
            return appdash.app.index()

        @app.route('/<path>')
        def static_file(path):
            return send_from_directory(os.path.join(dir_path, '../web/dist'), path)

        @app.route('/api')
        def api_index():
            base_url = "{}://{}/api".format(request.scheme, request.host)
            results = {}
            for config in settings.get_all_job_configs():
                name = config['name']
                results[name] = {
                    'url': '{}/items?jobname={}'.format(base_url, name),
                    'name': config.get('view', name),
                    'cron': config.get('cron', ''),
                }
            basic_info = {
                "yaml_config": '{}/_{}'.format(base_url, 'yaml'),
                "items": results,
            }
            return jsonify(basic_info)

        @app.route('/api/_yaml')
        def get_yaml():
            with open(settings.path, 'r') as stream:
                yaml_dict = yaml.load(stream)
            return jsonify(yaml_dict)

        @app.route('/api/items')
        def get_job_items():
            jobname = request.args.get('jobname')
            fmt = request.args.get('format', 'json')
            job = self.sched.jobs.get(jobname, None)
            if job is None:
                abort(404)
            originitems = job.store.iter(**request.args.to_dict())
            if len(originitems):
                if getattr(originitems[0], fmt, None) is None:
                    for f in ['html', 'markdown', 'json']:
                        if getattr(originitems[0], f, None) is not None:
                            fmt = f
                            break

            items = [getattr(i, fmt)() for i in originitems]
            columns = [c.key for c in job.store.item_class.__table__.columns if c.key != 'id']
            if fmt == 'markdown':
                # Markdown donot support open new tab
                items = [markdown2.markdown(i).replace('href=', 'target="_blank" href=') for i in items]
            return jsonify({'columns': columns, 'data': items, 'format': fmt, 'yaml': settings.get_job(jobname)})

    def run(self, ip='0.0.0.0', port=5000, **options):
        """Runs the application"""

        for _signal in [SIGINT, SIGTERM]:
            signal(_signal, self.stop)

        self.dash.run_server(host=ip, port=port, **options)

    def stop(self, signal, frame):
        logger.info('Server Stopped')
        exit()

if __name__ == '__main__':
    from trackupdates import Scheduler
    Server(Scheduler('examples/githubtrending.yaml')).run()
