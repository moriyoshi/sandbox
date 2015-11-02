from pyramid.view import view_config
from pyramid.config import Configurator
from .interfaces import IService

@view_config(route_name='pyspa.index', renderer='index.mako')
def index(context, request):
    remote_addr = request.service.get_remote_addr(request)
    return {'message':'hello, world!', 'remote_addr':remote_addr}

def paster_main(global_config, **local_config):
    settings = dict(global_config, **local_config)
    config = Configurator(settings=settings)
    config.include('pyramid_mako')
    config.include('.component')
    config.add_request_method(lambda request: request.registry.queryUtility(IService), 'service', reify=True)
    config.add_route('pyspa.index', '/')
    config.scan('.')
    return config.make_wsgi_app()
