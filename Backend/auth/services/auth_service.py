from zope.interface import Interface, Attribute

class IAuthService(Interface):
    database = Attribute("The database client used by the service")

class ILoginService(IAuthService):
    def login_user(data):
        pass
        
    def login_and_set_cookie(data, response):
        pass
        
    def get_current_user(request):
        pass

class IRegisterService(IAuthService):
    def signup_user(data):
        pass
        
    def signup_driver(data):
        pass