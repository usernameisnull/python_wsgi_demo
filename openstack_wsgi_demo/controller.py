# encoding: utf-8
import httplib
import json
import webob.dec
from openstack_wsgi_demo import req_processor
import wsgi_common as wsgi
from webob import Response
import six

CONTEXT_ENV = 'openstack.context'

class ControllerMetaclass(type):
    """Controller metaclass.

    This metaclass automates the task of assembling a dictionary
    mapping action keys to method names.
    """
    # 第一个参数是类,其他参数是传递给构造函数的
    def __new__(mcs, name, bases, cls_dict):
        """Adds the wsgi_actions dictionary to the class."""

        # Find all actions
        actions = {}
        extensions = []
        # start with wsgi actions from base classes
        for base in bases:
            actions.update(getattr(base, 'wsgi_actions', {}))
        for key, value in cls_dict.items():
            if not callable(value):
                continue
            if getattr(value, 'wsgi_action', None):
                actions[value.wsgi_action] = key
            elif getattr(value, 'wsgi_extends', None):
                extensions.append(value.wsgi_extends)

        # Add the actions and extensions to the class dict
        cls_dict['wsgi_actions'] = actions
        cls_dict['wsgi_extensions'] = extensions
        print "="*50, 'cls_dict: %s, type(cls_dict): %s' % (cls_dict, type(cls_dict))
        print "mcs: %s, name: %s, bases: %s, cls_dict: %s" % (mcs, name, base, cls_dict)
        return super(ControllerMetaclass, mcs).__new__(mcs, name, bases,
                                                       cls_dict)
@six.add_metaclass(ControllerMetaclass)
class Controller(object):
    def __init__(self):
        # TODO
        print '-'*20, 'app启动时,3). in Controller.__init__'
        self.version = "0.1"
        self.version1 = "0.2"
        print "*"*50, self.aa.wsgi_action

    @wsgi.action('aabbcc')
    def aa(self, context, req):
        print '-' * 20, 'app被访问时,8). in Controller.index'

        response = Response(request=req,
                            status=httplib.MULTIPLE_CHOICES,
                            content_type='application/json')
        response.body = json.dumps(dict(versions=self.version))
        return response
    
    def version(self, context, req):
        print '-' * 20, 'app被访问时,8). in Controller.aa'

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
        print '-' * 20, 'app被访问时,7). in Controller.__call__, request: %r, request.__class__: %s' % (request, request.__class__)
        # request.__class__: request.__class__: <class 'webob.request.Request'>
        context = req_processor.process_req(request)
        print '='*50,"action is : %s" % context['action'] 

        # reflect invoke method
        method = getattr(self, context['action'])

        # TODO
        return method(context, request)


def create_resource():
    return Controller()
