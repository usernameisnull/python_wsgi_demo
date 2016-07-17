# encoding: utf-8
import sys
from oslo_service import service
from oslo_config import cfg
from paste import deploy
import eventlet_server as wsgi
from oslo_concurrency import processutils
from oslo_utils import importutils

import os
CONF = cfg.CONF


class ConfigNotFound(Exception):
    message = "Could not find config at %(path)s"


def find_config(config_path):
    """Find a configuration file using the given hint.

    :param config_path: Full or relative path to the config.
    :returns: Full path of the config, if it exists.
    :raises: `cinder.exception.ConfigNotFound`
    core_opts = [
    cfg.StrOpt('api_paste_config',
                default="api-paste.ini",
                help='File name for the paste.deploy config for cinder-api'),
    cfg.StrOpt('state_path',
                default='/var/lib/cinder',
                deprecated_name='pybasedir',
                help="Top-level directory for maintaining cinder's state"), ]
    """
    possible_locations = [
        config_path,
        #os.path.join(CONF.state_path, "etc", "cinder", config_path),
        #os.path.join(CONF.state_path, "etc", config_path),
        #os.path.join(CONF.state_path, config_path),
        #"/etc/cinder/%s" % config_path,
    ]

    for path in possible_locations:
        if os.path.exists(path):
            return os.path.abspath(path)

    raise ConfigNotFound(path=os.path.abspath(config_path))

class Loader(object):
    """Used to load WSGI applications from paste configurations."""
    # core_opts = [
    # cfg.StrOpt('api_paste_config',
    #            default="api-paste.ini",
    #            help='File name for the paste.deploy config for cinder-api'),
    # cfg.StrOpt('state_path',
    #            default='/var/lib/cinder',
    #            deprecated_name='pybasedir',
    #            help="Top-level directory for maintaining cinder's state"), ]
    def __init__(self, config_path=None):
        """Initialize the loader, and attempt to find the config.

        :param config_path: Full or relative path to the paste config.
        :returns: None

        """
        config_path = config_path or CONF.api_paste_config
        #config_path = './api-paste.ini'
        self.config_path = find_config(config_path)

    def load_app(self, name): # name = 'osapi_volume'
        """Return the paste URLMap wrapped WSGI application.

        :param name: Name of the application to load.
        :returns: Paste URLMap object wrapping the requested application.
        :raises: `cinder.exception.PasteAppNotFound`

        """
        try:
            return deploy.loadapp("config:%s" % self.config_path, name=name)  # self.config_path = /etc/cinder/api-paste.ini
        except LookupError:
            raise Exception


class WSGIService(service.ServiceBase):
    """Provides ability to launch API from a 'paste' configuration."""
    # server = service.WSGIService('osapi_volume')
    def __init__(self, name, loader=None):
        """Initialize, but do not start the WSGI server.

        :param name: The name of the WSGI server given to the loader.
        :param loader: Loads the WSGI application using the given name.
        :returns: None

        """
        self.name = name
        self.manager = self._get_manager()
        self.loader = loader or Loader('./api-paste.ini')
        self.app = self.loader.load_app(name)   # name = osapi_volume
        self.host = getattr(CONF, '%s_listen' % name, "0.0.0.0")
        self.port = getattr(CONF, '%s_listen_port' % name, 8080)
        self.workers = (getattr(CONF, '%s_workers' % name, None) or
                        processutils.get_worker_count())
        if self.workers and self.workers < 1:
            worker_name = '%s_workers' % name
            msg = (("%(worker_name)s value of %(workers)d is invalid, "
                     "must be greater than 0.") %
                   {'worker_name': worker_name,
                    'workers': self.workers})
            raise Exception
        # setup_profiler(name, self.host)

        self.server = wsgi.Server(name,
                                  self.app,
                                  host=self.host,
                                  port=self.port)

    def _get_manager(self):
        """Initialize a Manager object appropriate for this service.

        Use the service name to look up a Manager subclass from the
        configuration and initialize an instance. If no class name
        is configured, just return None.

        :returns: a Manager instance, or None.

        """
        fl = '%s_manager' % self.name # self.name = 'osapi_volume'
        if fl not in CONF:
            return None

        manager_class_name = CONF.get(fl, None)
        if not manager_class_name:
            return None

        manager_class = importutils.import_class(manager_class_name)
        return manager_class()

    def start(self):
        """Start serving this service using loaded configuration.

        Also, retrieve updated port number in case '0' was passed in, which
        indicates a random port should be used.

        :returns: None

        """
        if self.manager:
            self.manager.init_host()
        self.server.start()
        self.port = self.server.port

    def stop(self):
        """Stop serving this API.

        :returns: None

        """
        self.server.stop()

    def wait(self):
        """Wait for the service to stop serving this API.

        :returns: None

        """
        self.server.wait()

    def reset(self):
        """Reset server greenpool size to default.

        :returns: None

        """
        self.server.reset()


def process_launcher():
    return service.ProcessLauncher(CONF)


def main():
    CONF(sys.argv[1:], project='demo',
         version='1.0')

    launcher = process_launcher()
    # 'osapi_volume' 需要与api-paste.ini里section的name对应
    server = WSGIService('osapi_volume')
    launcher.launch_service(server, workers=server.workers)
    launcher.wait()

if __name__ == '__main__':
    main()
