from Products.CMFCore.utils import getToolByName
PROFILE = 'profile-pas.plugins.facebook:default'


def common(context):
    setup = getToolByName(context, 'portal_setup')
    setup.runAllImportStepsFromProfile(PROFILE)
