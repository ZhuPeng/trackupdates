# -*- coding: utf-8 -*-
import yaml
from signal import signal, SIGINT, SIGTERM
from flask import Flask, request, jsonify, logging, abort
logger = logging.getLogger(__file__)


class Server:
    def __init__(self, sched):
        app = Flask(__name__)
        app.logger.setLevel(logging.ERROR)
        self.app = app
        self.sched = sched
        self.init_route()

    def init_route(self):
        app = self.app
        settings = self.sched.settings

        @app.route('/')
        def index():
            base_url = "{}://{}".format(request.scheme, request.host)
            results = {}
            for config in settings.get_all_job_configs():
                name = config['name']
                results[name] = {
                    'url': '{}/items/{}'.format(base_url, name),
                }
            basic_info = {
                "yaml_config": '{}/_{}'.format(base_url, 'yaml'),
                "items": results,
            }
            return jsonify(basic_info)

        @app.route('/_yaml')
        def get_yaml():
            with open(settings.path, 'r') as stream:
                yaml_dict = yaml.load(stream)
            return jsonify(yaml_dict)

        @app.route('/items/<jobname>')
        def get_job_items(jobname):
            job = self.sched.jobs.get(jobname, None)
            if job is None:
                abort(404)
            items = [i.json() for i in job.store.iter()]
            return jsonify(items)

    def run(self, ip='127.0.0.1', port=5000, **options):
        """Runs the application"""

        for _signal in [SIGINT, SIGTERM]:
            signal(_signal, self.stop)

        self.app.run(ip, port, **options)

    def stop(self, signal, frame):
        logger.info('Server Stopped')
        exit()

if __name__ == '__main__':
    from trackupdates import Scheduler
    Server(Scheduler('examples/githubtrending.yaml')).run()
