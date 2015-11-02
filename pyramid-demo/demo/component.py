from zope.interface import implementer
from .interfaces import IService

@implementer(IService)
class MyService(object):
    def __init__(self, config):
        pass

    def get_remote_addr(self, request):
        return request.remote_addr


def includeme(config):
    config.registry.registerUtility(
        MyService(config),
        IService
        )

