# encoding: utf-8
import routes.middleware
import webob.dec
import webob.exc
import routes
from openstack_wsgi_demo import controller as app_tmp


class Router(object):  # as wsgi app base class, solve the map url to resource

    def __init__(self, mapper=None):
        print '-'*20, 'app启动时,4). in Router.__init__'
        self.map = mapper  # create resource map
        self._router = routes.middleware.RoutesMiddleware(self._dispatch, self.map)  # register the url call back method

    @classmethod
    def factory(cls, global_conf, **local_conf):  # actual portal
        print '-'*20, 'app启动时,1). in Router.factory, cls: %s' % cls   # cls: <class 'openstack_wsgi_demo.router.APIRouter'>
        return cls()  # create app

    @webob.dec.wsgify  # convert request and response to wsgiful
    def __call__(self, req):  # callable object
        print '-' * 20, 'app被访问时,5). in Router.__call__'
        return self._router

    @staticmethod
    @webob.dec.wsgify
    def _dispatch(req):
        print '-' * 20, 'app被访问时,6). in Router._dispatch'
        # TODO
        match = req.environ['wsgiorg.routing_args'][1]
        if not match:
            return webob.exc.HTTPNotFound()
        app = match['controller']
        return app


class APIRouter(Router):
    def __init__(self, mapper=None):
        print '-' * 20, 'app启动时,2). in APIRouter.__init__'
        if mapper is None:  # create mapper object
            mapper = routes.Mapper()

        tmp_resource = app_tmp.create_resource()  # create resource
        mapper.connect("/", controller=tmp_resource,  # create map
                       action="index",
                       conditions={'method': ['GET']})
        super(APIRouter, self).__init__(mapper)