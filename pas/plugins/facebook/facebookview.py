#python
import facebook as facebooklib

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


class FacebookView(BrowserView):
    """Graph api wrapper based on browserview"""
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._app_id = None
        self._app_secret = None
        self.wrapper = None
        self._settings = None

        self.redirect_uri = ""
        self.scope = ""
        self.state = None
        self.response_type = ""
        self.display = ""
        self.code = ""
        self._token = ""
        self._expire = ""

    def update(self):
        self.wrapper = facebooklib.GraphAPI(self.access_token, self.timeout)
        registry = component.queryUtility(IRegistry)
        self._settings = registry.forInterface(IFacebookAppSettings)
        if not self._app_id:
            self._app_id = self._settings.app_id
        if not self._app_secret:
            self._app_secret = self._settings.app_secret
        if not self.redirect_uri:
            self.redirect_uri = self.context.absolute_url()
        if not self.scope:
            self.scope = self._settings.scope

    @property
    def client_id(self):
        return self._app_id

    def get_access_token(self):
        return self._token
    
    def set_access_token(self, token):
        if 'access_token' in token:
            self._token = token["access_token"]
        else:
            self._token = token
        self.wrapper = facebooklib.GraphAPI(self._token, self.timeout)

    access_token = property(get_access_token, set_access_token)

    @property
    def timeout(self):
        return self._expire

    def get_object(self, id, **args):
        return self.wrapper.get_object(id, **args)

    def get_objects(self, ids, **args):
        return self.wrapper.get_object(ids, **args)

    def get_connections(self, id, connection_name, **args):
        return self.wrapper.get_connections(id, **args)

    def put_object(self, parent_object, connection_name, **data):
        return self.wrapper.put_object(parent_object, connection_name, **data)

    def put_wall_post(self, message, attachment={}, profile_id="me"):
        return self.wrapper.put_wall_post(message, attachment=attachment,
                                          profile_id=profile_id)

    def put_comment(self, object_id, message):
        return self.wrapper.put_comment(self, object_id, message)

    def put_like(self, object_id):
        return self.wrapper.put_like(self, object_id)

    def frequest(self, path, args=None, post_args=None):
        return self.wrapper.request(self, path, args=args, post_args=post_args)

    def fql(self, query, args=None, post_args=None):
        return self.wrapper.fql(query, args=args, post_args=post_args)

    def extend_access_token(self):
        return self.wrapper.extends_access_token(self._app_id,
                                                 self._app_secret)

    def get_user_from_cookie(self):
        cookies = self._request.cookies
        return facebooklib.get_user_from_cookie(cookies,
                                                self._app_id, self._app_secret)

    def parse_signed_request(self, signed_request):
        return facebooklib.parse_signed_request(signed_request, self._app_secret)
    
    def auth_url(self, redirect_uri=None, scope=None, state=None):
        if not redirect_uri:
            redirect_uri = self.redirect_uri
        if not scope:
            scope = self.scope
        return facebooklib.auth_url(self._app_id, redirect_uri,
                                    perms=scope, state=state)

    def get_access_token_from_code(self, code, redirect_uri=None):
        if redirect_uri is None:
            redirect_uri = self.redirect_uri
        return facebooklib.get_access_token_from_code(code, redirect_uri,
                                              self._app_id, self._app_secret)

    def get_app_access_token(self):
        return facebooklib.get_app_access_token(self._app_id, self._app_secret)
