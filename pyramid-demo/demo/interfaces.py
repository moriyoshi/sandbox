from zope.interface import Interface

class IService(Interface):
    def get_remote_addr(request):
        pass
