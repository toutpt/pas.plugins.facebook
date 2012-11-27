from zope.i18nmessageid import MessageFactory
facebook_message_factory = MessageFactory("pas.plugins.facebook")
_ = facebook_message_factory


oauthdialog_redirect_uri_desc = _(u"oauthdialog_redirect_uri_desc",
  default = u"""The URL to redirect to after the user clicks a button in the\
dialog. The URL you specify must be a URL of with the same Base Domain\
as specified in your app's settings, a Canvas URL of the form \
https://apps.facebook.com/YOUR_APP_NAMESPACE or a Page Tab URL of the form \
https://www.facebook.com/PAGE_USERNAME/app_YOUR_APP_ID""")

oauthdialog_scope_desc =_(u"oauthdialog_scope_desc",
  default=u"""A comma separated list of permission names which you would like \
the user to grant your application. Only the permissions which the user has not\
already granted your application will be shown""")

oauthdialog_state_desc = _(u"oauthdialog_state_desc",
  default=u"""A unique string used to maintain application state between the \
request and callback. When Facebook redirects the user back to your \
redirect_uri, this parameter's value will be included in the response. \
You should use this to protect against Cross-Site Request Forgery.""")

oauthdialog_response_type_desc = _(u"oauthdialog_response_type_desc",
  default=u"""The requested response type, one of code or token. Defaults to \
code. If left unset, or set to code the Dialog's response will include an \
OAuth code which can be exchanged for an access token as per the server-side 
\authentication flow. If set to token, the Dialog's response will include an \
oauth user access token in the fragment of the URL the user is redirected \
to - as per the client-side authentication flow.""")

oauthdialog_display_desc = _(u"oauthdialog_display_desc",
  default=u"""The display mode with which to render the Dialog. One of page, \
popup or touch. Defaults to page when the user is using a desktop browser or \
the dialog is invoked on the www.facebook.com domain. Defaults to touch when \
the user is using a mobile browser or the dialog is invoked on the \
m.facebook.com domain. In page mode, the OAuth dialog is displayed in the full \
Facebook chrome. In 'popup' mode, the OAuth dialog is displayed in a form \
suitable for embedding in a popup window. This parameter is automatically \
specified by most Facebook SDK, so may not need to be set explicitly.
""")
