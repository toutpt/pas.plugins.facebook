#python
import urllib

#zope
from zope import component
from zope import interface
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from Products.Five.browser import BrowserView

#plone
from plone.registry.interfaces import IRegistry

#internal
from pas.plugins.facebook import i18n
from pas.plugins.facebook import permissions

_ = i18n.facebook_message_factory


display_mode_list = ['page', 'popup', 'touch']
DisplayModeVocabulary = SimpleVocabulary([
  SimpleTerm(term, term, unicode(term)) for term in display_mode_list
])

response_type_list = ['code', 'token']
ResponseTypeVocabulary = SimpleVocabulary([
  SimpleTerm(term, term, unicode(term)) for term in response_type_list
])

scopes = permissions.extended_permissions_list + \
         permissions.user_permissions_list + \
         permissions.friends_permissions_list

ScopeVocabulary = SimpleVocabulary([
  SimpleTerm(term, term, unicode(term)) for term in scopes
])


class IOAuthDialogParameters(interface.Interface):
    """OAuth dialog parameters"""

    client_id = schema.ASCIILine(title=_(u"App ID"),
                                 required=True,
                                 )

    redirect_uri = schema.URI(title=_(u"Redirect URI"),
                              description=i18n.oauthdialog_redirect_uri_desc,
                              required=True,
                              )

    scope = schema.ASCIILine(title=_(u"Scope"),
                             description=i18n.oauthdialog_scope_desc,
                             required=False,
                             )

    state = schema.ASCIILine(title=_(u"State"),
                             description=i18n.oauthdialog_state_desc,
                             required=False,
                             )

    response_type = schema.Choice(title=_(u"Response Type"),
                             description=i18n.oauthdialog_response_type_desc,
                             required=False,
                             vocabulary=ResponseTypeVocabulary,
                             )

    display = schema.Choice(title=_(u"Display mode"),
                            description=i18n.oauthdialog_display_desc,
                            required=False,
                            vocabulary=DisplayModeVocabulary,
                            )  #default to 'page'


class IFacebookAppSettings(interface.Interface):
    """App settings.
    https://developers.facebook.com/apps/
    """

    app_id = schema.ASCIILine(title=_(u"App ID"),
                              required=True,
                              )

    app_secret = schema.ASCIILine(title=_(u"App Secret"),
                                  required=True,
                                  )

    scope = schema.List(title=_(u"Scope"),
                             description=i18n.oauthdialog_scope_desc,
                             required=False,
                             value_type=schema.Choice(title=_(u"Scope"),
                                                  vocabulary=ScopeVocabulary),
                        )


class FacebookAppSettingsView(BrowserView):
    interface.implements(IFacebookAppSettings)
    def __init__(self, context, request):
        self.context = context 
        self.request = request


class LoginURLBuilder(BrowserView):
    """This page url"""
    interface.implements(IOAuthDialogParameters)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.client_id = ""
        self.redirect_uri = ""
        self.scope = ""
        self.state = None
        self.response_type = ""
        self.display = ""
        self._settings = None
        #self._login_url = "https://www.facebook.com/dialog/oauth/?"
        self.code = ""

    def get_login_url(self):
        self.update()
        return facebook.auth_url(self.client_id,
                                 self.redirect_uri,
                                 perms=self.scope,
                                 state=self.state)

    def update(self):
        registry = component.queryUtility(IRegistry)
        self._settings = registry.forInterface(IFacebookAppSettings)
        if not self.client_id:
            self.client_id = self._settings.app_id
        if not self.redirect_uri:
            self.redirect_uri = self.context.absolute_url()
        if not self.scope:
            self.scope = self._settings.scope

    def get_token_url(self):
        self.update()
        return url
