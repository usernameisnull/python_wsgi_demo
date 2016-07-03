# encoding: utf-8
import httplib
import json
import webob.dec
from openstack_wsgi_demo import req_processor

from webob import Response

CONTEXT_ENV = 'openstack.context'


class Controller(object):
    def __init__(self):
        # TODO
        print '-'*20, 'app启动时,3). in Controller.__init__'
        self.version = "0.1"
        self.version1 = "0.2"

    def index(self, context, req):
        print '-' * 20, 'app被访问时,8). in Controller.index'

        response = Response(request=req,
                            status=httplib.MULTIPLE_CHOICES,
                            content_type='application/json')
        response.body = json.dumps(dict(versions=self.version))
        return response

    # get
    def get(self, context, req):
        id = req_processor.get_router_param(req, 'tmp_id')
        response = Response(request=req,
                            status=httplib.MULTIPLE_CHOICES,
                            content_type='application/json')
        response.body = json.dumps(dict(versions=self.version1))
        return response

    # put
    def put(self, context, req):
        response = Response(request=req,
                            status=httplib.MULTIPLE_CHOICES,
                            content_type='application/json')
        response.body = json.dumps(dict(versions=self.version1))
        return response

    @webob.dec.wsgify
    def __call__(self, request):
        print '-' * 20, 'app被访问时,7). in Controller.__call__'
        print '-' * 20, 'app被访问时,7). in Controller.__call__, request: %r, request.__class__: %s' % (request, request.__class__)
        # request.__class__: request.__class__: <class 'webob.request.Request'>
        context = req_processor.process_req(request)

        # reflect invoke method
        method = getattr(self, context['action'])

        # TODO
        return method(context, request)


def create_resource():
    return Controller()