#python
import logging
import urllib
import urlparse
import copy
import json

#zope
from zope import component
from zope import interface
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from BTrees.OOBTree import OOBTree
from OFS.Cache import Cacheable
from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService import plugins
from Products.PluggableAuthService import interfaces
from Products.PluggableAuthService import utils

#internal
from pas.plugins.facebook import facebookview

logger = logging.getLogger('pas.plugins.facebook')


class UserProperties(object):
    def __init__(self, username, token):
        graph_url = "https://graph.facebook.com/%s?access_token=%s"
        self.username = username
        self.token = token
        self.graph_url =   graph_url % (username, token)
        self.user_info = {}

    def update(self):
        self.update_token()
        self.user_info = json.loads(urllib.urlopen(self.graph_url).read())

    def update_token(self):
        if self.token.startswith('access_token'):
            query = urlparse.parse_qs(self.token)
            self.token = query['access_token'][0]
            self.expire = ""

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            pass
        try:
            return self.user_info[name]
        except KeyError:
            raise AttributeError(name)


class IPASPlugin(interface.Interface):
    """Marker interface"""


class PASPlugin(plugins.BasePlugin.BasePlugin):
    """This plugin check if the current user"""

    interface.implements(interfaces.plugins.IAuthenticationPlugin,
                         interfaces.plugins.IUserEnumerationPlugin,
                         interfaces.plugins.IPropertiesPlugin,
                         interfaces.plugins.IExtractionPlugin,
                         IPASPlugin)

    meta_type = 'Facebook IPropertiesPlugin'
    security = ClassSecurityInfo()

    def __init__(self, id, title=None):
        self.id = id
        self.title = title
        self._activated = None
        self._v_blacklist_ids = []
        self.facebook_accounts = OOBTree()

    @property
    def activated(self):
        """Return True if webservice and pasplugin are activated"""
        if self._activated is not None:
            return self._activated
        return True

    security.declarePrivate('extractCredentials')
    def extractCredentials(self, request):
        fb = facebookview.FacebookView(self, self.REQUEST)
        user = fb.get_user_from_cookie()

        info = {}

        return info

    security.declarePrivate('authenticateCredentials')
    def authenticateCredentials(self, credentials):
        """See IAuthenticationPlugin."""
        username = credentials.get("facebook_username")
        userid= credentials.get("facebook_userid")
        if username is None:
            return None
        else:
            return userid, username

    security.declarePrivate('enumerateUsers')
    def enumerateUsers( self
                      , id=None
                      , login=None
                      , exact_match=False
                      , sort_by=None
                      , max_results=None
                      , **kw
                      ):
        """ See IUserEnumerationPlugin.
        """

        if not self.activated:return []

        if isinstance( id, basestring ):
            id = [ str(id) ]

        if isinstance( login, basestring ):
            login = [ str(login) ]

        lookup_ids = []
        if login is not None and id is None:
            lookup_ids = login
        elif id is not None and login is None:
            lookup_ids = id

        res = {}
        for i in lookup_ids:
            if i in res.keys():
                continue
            if self.isInBlacklist(i):
                continue
            logger.info('enumerateUsers not cached %s'%i)
            if i in self.facebook_accounts:
                res[i] = self.facebook_accounts[i]

        user_info = []
        plugin_id = self.getId()
        e_url = '%s/manage_users' % plugin_id
        for i in res.keys():
            webinfo = res[i]
            if not webinfo:
                continue
            qs = 'user_id=%s' % i
            info = { 'id' : i
                      , 'login' : i #TODO: push username here
                      , 'pluginid' : plugin_id
                      , 'editurl' : '%s?%s' % (e_url, qs)
                   } 
            user_info.append(info)

        if len(user_info) == 0:
            for i in lookup_ids:
                self.addToBlacklist(i)

        return user_info

    security.declarePrivate('getPropertiesForUser')
    def getPropertiesForUser(self, user, request=None):
        """ See IPropertiesPlugin.
        """
        if not self.activated:return {}
        user_id = user.getUserId()
        user_name = user.getUserName()

        properties = {}
        if user_id in self.facebook_accounts:
            token = self.facebook_accounts[user_id]
            user = UserProperties(user_name, token)
            user.update()
#            import pdb;pdb.set_trace()
            properties= {'email': user.email,
                         'fullname': user.name
                        }
        logger.info(properties)
        return properties

    def addToBlacklist(self, key):
        if not hasattr(self, '_v_blacklist_ids'):
            setattr(self, '_v_blacklist_ids', [])
        self._v_blacklist_ids.append(key)
    
    def isInBlacklist(self, key):
        if not hasattr(self, '_v_blacklist_ids'):
            setattr(self, '_v_blacklist_ids', [])
        return key in self._v_blacklist_ids


class CachedPASPlugin(PASPlugin, Cacheable):
    """Cacheable Version"""
    security = ClassSecurityInfo()

    security.declarePrivate('enumerateUsers')
    def enumerateUsers( self
                      , id=None
                      , login=None
                      , exact_match=False
                      , sort_by=None
                      , max_results=None
                      , **kw
                      ):

        if not self.activated:return []
        view_name = 'FacebookEnumerateUsers'
        #logger.info('enumerateUsers cached')

        if isinstance( id, basestring ):
            id = [ str(id) ]

        if isinstance( login, basestring ):
            login = [ str(login) ]

        lookup_ids = []
        if login is not None and id is None:
            lookup_ids = login
        elif id is not None and login is None:
            lookup_ids = id

        # Look in the cache first...
        if len(lookup_ids)==0:
            return []

        keywords = {'id' : lookup_ids[0]}

        cached_info = self.ZCacheable_get( view_name=view_name
                                         , keywords=keywords
                                         , default="not_in_cache"
                                         )

        if cached_info != "not_in_cache":
            return tuple(cached_info)

        user_info = PASPlugin.enumerateUsers(self, id=id
                      , login=login
                      , exact_match=exact_match
                      , sort_by=sort_by
                      , max_results=max_results
                      , **kw
                      )

        self.ZCacheable_set(user_info,
                            view_name=view_name,
                            keywords=keywords)

        return tuple( user_info )

    security.declarePrivate('getPropertiesForUser')
    def getPropertiesForUser(self, user, request=None):
        """ See IPropertiesPlugin.
        """

        if not self.activated:return {}
        user_name = str(user.getUserName())
        keywords = {'user_name':str(user_name)}
        view_name = 'FacebookgetPropertiesForUser'
        cached_properties = self.ZCacheable_get( view_name=view_name
                                         , keywords=keywords
                                         , default="not_in_cache"
                                         )
        if cached_properties != "not_in_cache":
            return cached_properties
        
        properties = PASPlugin.getPropertiesForUser(self, user,
                                                            request=request)

        self.ZCacheable_set(properties, view_name=view_name,
                            keywords=keywords)

        return properties
    #
    #   ZMI
    #
    manage_options = ( ( { 'label': 'Users', 
                           'action': 'manage_users', }
                         ,
                       )
                     + PASPlugin.manage_options
                     + Cacheable.manage_options
                     )

InitializeClass(CachedPASPlugin)
