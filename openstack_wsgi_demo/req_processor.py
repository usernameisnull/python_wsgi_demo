CONTEXT_ENV = 'openstack.context'


def process_req(request):
    """
    Parse the request,return the context
    :param request:the request object

    """
    arg_dict = request.environ['wsgiorg.routing_args'][1]

    context = request.environ.get(CONTEXT_ENV, {})
    context['query_string'] = dict(request.params.iteritems())
    context['headers'] = dict(request.headers.iteritems())
    context['body'] = request.body
    context['path'] = request.environ['PATH_INFO']
    context['body-file'] = request.body_file
    context['action'] = arg_dict.pop('action')

    # print context['query_string']
    # print context['headers']
    # print context['path']
    # print context['body']
    # print context['action']

    return context


def get_router_param(request, key):
    """
    get the router url param,eg:resource id
    :param request:the request object
    :param key:the args key
    """
    arg = request.environ['wsgiorg.routing_args'][1][key]
    return arg