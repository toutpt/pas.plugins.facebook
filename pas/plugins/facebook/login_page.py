#python
import urllib
import urlparse
import json

#zope
from zope import component
from AccessControl.SecurityManagement import newSecurityManager
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

#plone
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName

#internal
from pas.plugins.facebook.oauthdialog import LoginURLBuilder, IFacebookAppSettings
from pas.plugins.facebook import i18n
from pas.plugins.facebook import permissions

_ = i18n.facebook_message_factory


class Login(BrowserView):
    """login page"""

    def __call__(self):
        url_builder = LoginURLBuilder(self.context, self.request)
        url = self.context.absolute_url()
        url_builder.redirect_uri = '%s/loggedin_facebook' % url
        self.request.response.redirect(url_builder.get_login_url())
        return u""


class LoggedIn(BrowserView):
    """save the token to session used by the pas plugin"""
    def __call__(self):
        self.update()
        status = IStatusMessage(self.request)
        status.add(_(u"logged in with facebook"), 'info')
        self.request.response.redirect(self.context.absolute_url())
        return u""

    def update(self):
        #code is in the request, we should get the token, lets use this one
        self.sudo_save()

    def sudo_save(self, ):
        """store the token associate to this userid"""
        user = AuthenticatedUserBasicInfo(self.context, self.request)
        user.update()
        #get the plugin and do a save of this userid: token entry
        acl_users = getToolByName(self.context, 'acl_users')
        admin=acl_users.getUserById('facebook')
        newSecurityManager(self.request, admin)
        tokens = getattr(acl_users.facebook, 'facebook_token', None)
        if not tokens:
            acl_users.facebook.facebook_token = {}
            tokens = acl_users.facebook.facebook_token
        if user.id not in tokens or tokens[user.id] != user.token:
            tokens[user.id] = user.token_raw


class TokenExtractor(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.code = None
        self.token = None
        self.token_raw = ""
        self.expire = None

    def update(self):
        if not self.code and not self.token:
            self.code = self.request.form.get('code', None)
        if self.code and not self.token:
            self.update_token()

    def update_token(self):
        url_builder = LoginURLBuilder(self.context, self.request)
        url_builder.code = self.code
        url = self.context.absolute_url()
        url_builder.redirect_uri = '%s/loggedin_facebook' % url
        filehandle = urllib.urlopen(url_builder.get_token_url())
        
        qs = filehandle.read()
        query = urlparse.parse_qs(qs)
        if 'access_token' in query:
            self.token = query['access_token'][0]
            self.token_raw = qs
#            self.expire = query['expire']


class AuthenticatedUserBasicInfo(TokenExtractor):
    def __init__(self, context, request):
        TokenExtractor.__init__(self, context, request)
        self._user = None

    def update(self):
        TokenExtractor.update(self)
        if self._user is None and self.token:
            self._user = self._get_user()

    def _get_user(self):
        graph_url = "https://graph.facebook.com/me?access_token="+self.token
        user = json.loads(urllib.urlopen(graph_url).read())
        return user

    def __getattribute__(self, name):
        if name in permissions.basic_info_list and self._user:
            return self._user[name]
        return object.__getattribute__(self, name)

