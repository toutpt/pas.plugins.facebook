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


class LoginURLBuilder(BrowserView):
    """This page url"""
    interface.implements(IOAuthDialogParameters)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.client_id = ""
        self.redirect_uri = ""
        self.scope = ""
        self.state = ""
        self.response_type = ""
        self.display = ""
        self._settings = None
        self._login_url = "https://www.facebook.com/dialog/oauth/?"

        self._token_url = "https://graph.facebook.com/oauth/access_token?"
        self.code = ""

    def get_login_url(self):
        self.update()
        kwargs = self._get_login_parameters()
        url = self._login_url + urllib.urlencode(kwargs)
        return url

    def update(self):
        registry = component.queryUtility(IRegistry)
        self._settings = registry.forInterface(IFacebookAppSettings)

    def _get_login_parameters(self):
        if not self.client_id:
            self.client_id = self._settings.app_id
        if not self.redirect_uri:
            self.redirect_uri = self.context.absolute_url()
        kwargs = {"client_id": self.client_id,
                  "redirect_uri": self.redirect_uri}
        for attr in ('client_id', 'redirect_uri', 'scope', 'state',
                     'response_type', 'display'):
            value = getattr(self, attr)
            if value:
                kwargs[attr] = value
        if 'scope' not in kwargs:
            kwargs['scope'] = ','.join(self._settings.scope)
        return kwargs

    def _get_token_parameters(self):
        login_params = self._get_login_parameters()
        kwargs = {}
        kwargs['client_id'] = login_params['client_id']
        kwargs['redirect_uri'] = login_params['redirect_uri']
        kwargs['code'] = self.code
        kwargs['client_secret'] = self._settings.app_secret
        return kwargs

    def get_token_url(self):
        self.update()
        kwargs = self._get_token_parameters()
        url = self._token_url + urllib.urlencode(kwargs)
        return url
