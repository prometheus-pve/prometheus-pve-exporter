"""
HTTP API for Proxmox VE prometheus collector.
"""

import logging
import time
from functools import partial
import fnmatch

import gunicorn.app.base
from prometheus_client import CONTENT_TYPE_LATEST, Summary, Counter, generate_latest
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import InternalServerError
from pve_exporter.collector import collect_pve


class PveExporterApplication:
    """
    Proxmox VE prometheus collector HTTP handler.
    """

    def __init__(self, config, collectors, logger):
        self._config = config
        self._collectors = collectors
        self._log = logger

        self._duration = Summary(
            'pve_collection_duration_seconds',
            'Duration of collections by the PVE exporter',
            ['module'],
        )
        self._errors = Counter(
            'pve_request_errors_total',
            'Errors in requests to PVE exporter',
            ['module'],
        )

        # Initialize metrics.
        for module in config.keys():
            # pylint: disable=no-member
            self._errors.labels(module)
            # pylint: disable=no-member
            self._duration.labels(module)

    def target_allowed(self, target, allowed_targets):
        """
        Check if target is allowed using simple pattern matching.
        """
        # localhost always allowed
        if target in ['localhost', '127.0.0.1', '::1']:
            return True, "localhost always allowed"
        
        # If no whitelist only localhost allowed
        if not allowed_targets:
            return False, "No allowed_targets specified, only localhost allowed"
        
        for pattern in allowed_targets:
            if fnmatch.fnmatch(target, pattern):
                return True, f"Matched pattern: {pattern}"
        
        return False, "Target not in whitelist"

    def on_pve(self, module='default', target='localhost', cluster='1', node='1'):
        """
        Request handler for /pve route
        """

        if module not in self._config:
            response = Response(f"Module '{module}' not found in config")
            response.status_code = 400
            return response

        # Get allowed_targets from config
        module_config = self._config[module]
        allowed_targets = module_config.get('allowed_targets')

        # Validate target against whitelist 
        is_allowed, reason = self.target_allowed(target, allowed_targets)

        if not is_allowed:
            # Detailed logging (for admin)
            self._log.warning(
                "Target '%s' rejected for module '%s'. Reason: %s. "
                "Allowed patterns: %s",
                target, module, reason, allowed_targets or "[]"
            )
            
            # Minimal error (for potential attacker)
            response = Response("Forbidden")
            response.status_code = 403
            return response
        
        # Filter out allowed_targets before passing to ProxmoxAPI
        api_config = {k: v for k, v in module_config.items() if k != 'allowed_targets'}

        start = time.time()
        output = collect_pve(
            api_config,
            target,
            cluster.lower() not in ['false', '0', ''],
            node.lower() not in ['false', '0', ''],
            self._collectors
        )
        response = Response(output)
        response.headers['content-type'] = CONTENT_TYPE_LATEST
        self._duration.labels(module).observe(time.time() - start)

        return response

    def on_metrics(self):
        """
        Request handler for /metrics route
        """

        response = Response(generate_latest())
        response.headers['content-type'] = CONTENT_TYPE_LATEST

        return response

    def on_index(self):
        """
        Request handler for index route (/).
        """

        response = Response(
            """<html>
            <head><title>Proxmox VE Exporter</title></head>
            <body>
            <h1>Proxmox VE Exporter</h1>
            <p>Visit <code>/pve?target=1.2.3.4</code> to use.</p>
            </body>
            </html>"""
        )
        response.headers['content-type'] = 'text/html'

        return response

    def view(self, endpoint, values, args):
        """
        Werkzeug views mapping method.
        """

        allowed_args = {
            'pve': ['module', 'target', 'cluster', 'node']
        }

        view_registry = {
            'index': self.on_index,
            'metrics': self.on_metrics,
            'pve': self.on_pve,
        }

        params = dict(values)
        if endpoint in allowed_args:
            params.update({key: args[key] for key in allowed_args[endpoint] if key in args})

        try:
            return view_registry[endpoint](**params)
        except Exception as error:  # pylint: disable=broad-except
            self._log.exception("Exception thrown while rendering view")
            self._errors.labels(args.get('module', 'default')).inc()
            raise InternalServerError from error

    @Request.application
    def __call__(self, request):
        url_map = Map([
            Rule('/', endpoint='index'),
            Rule('/metrics', endpoint='metrics'),
            Rule('/pve', endpoint='pve'),
        ])

        urls = url_map.bind_to_environ(request.environ)
        view_func = partial(self.view, args=request.args)
        return urls.dispatch(view_func, catch_http_exceptions=True)


class StandaloneGunicornApplication(gunicorn.app.base.BaseApplication):
    """
    Copy-paste from https://docs.gunicorn.org/en/stable/custom.html
    """

    # 'init' and 'load' methods are implemented by WSGIApplication.
    # pylint: disable=abstract-method

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def start_http_server(config, gunicorn_options, collectors):
    """
    Start a HTTP API server for Proxmox VE prometheus collector.
    """

    # If running under gunicorn, reuse the gunicorn.error logger for the
    # exporter application.
    # https://trstringer.com/logging-flask-gunicorn-the-manageable-way/
    logger = logging.getLogger('gunicorn.error')
    app = PveExporterApplication(config, collectors, logger)
    StandaloneGunicornApplication(app, gunicorn_options).run()