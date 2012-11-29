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
from pas.plugins.facebook import facebookview

_ = i18n.facebook_message_factory


class Login(facebookview.FacebookView):
    """login page"""

    def __call__(self):
        """doc string"""
        self.update()
        self.redirect_uri = '%s/loggedin_facebook' % self.context.absolute_url()
        self.request.response.redirect(self.auth_url())
        return u""


class LoggedIn(facebookview.FacebookView):
    """save the token to session used by the pas plugin"""
    def __call__(self):
        self.update()
        status = IStatusMessage(self.request)
        status.add(_(u"logged in with facebook"), 'info')
        self.request.response.redirect(self.context.absolute_url())
        return u""

    def update(self):
        super(LoggedIn, self).update()
        #code is in the request, we should get the token, lets use this one
        self.sudo_save()

    def sudo_save(self):
        """store the token associate to this userid"""
        code = self.request.get('code', '')
        token_info = self.get_access_token_from_code(code)
        self.access_token = token_info
        user = self.get_object("me")
        user_id = user["id"]

        #get the plugin and do a save of this userid: token entry
        acl_users = getToolByName(self.context, 'acl_users')
        admin=acl_users.getUserById('facebook')
        newSecurityManager(self.request, admin)
        tokens = acl_users.facebook.facebook_accounts
        if user_id not in tokens or tokens[user_id] != user.token:
            tokens[user_id] = self.access_token


class Loggout(BrowserView):
    def __call__(self):
        self.request.response.expireCookie("fb_user")
