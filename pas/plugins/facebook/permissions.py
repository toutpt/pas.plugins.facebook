from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

#https://developers.facebook.com/docs/reference/login/basic-info/
basic_info_list = [
  'id',
  'name',
  'first_name',
  'last_name',
  'link',
  'username',
  'gender',
  'locale',
]

#https://developers.facebook.com/docs/reference/login/extended-permissions/
extended_permissions_list = [
  'read_friendlists',
  'read_insights',
  'read_mailbox',
  'read_requests',
  'read_stream',
  'xmpp_login',
  'ads_management',
  'create_event',
  'manage_friendlists',
  'manage_notifications',
  'user_online_presence',
  'friends_online_presence',
  'publish_checkins',
  'publish_stream',
  'rsvp_event',
]


#https://developers.facebook.com/docs/reference/login/user-friend-permissions/
user_permissions_list = [
  'user_about_me',
  'user_activities',
  'user_birthday',
  'user_checkins',
  'user_education_history',
  'user_events',
  'user_groups',
  'user_hometown',
  'user_interests',
  'user_likes',
  'user_location',
  'user_notes',
  'user_photos',
  'user_questions',
  'user_relationships',
  'user_relationship_details',
  'user_religion_politics',
  'user_status',
  'user_subscriptions',
  'user_videos',
  'user_website',
  'user_work_history',
  'email',
]

friends_permissions_list = [
  'friends_about_me',
  'friends_activities',
  'friends_birthday',
  'friends_checkins',
  'friends_education_history',
  'friends_events',
  'friends_groups',
  'friends_hometown',
  'friends_interests',
  'friends_likes',
  'friends_location',
  'friends_notes',
  'friends_photos',
  'friends_questions',
  'friends_relationships',
  'friends_relationship_details',
  'friends_religion_politics',
  'friends_status',
  'friends_subscriptions',
  'friends_videos',
  'friends_website',
  'friends_work_history',
]


ExtendedPermissionsVocabulary = SimpleVocabulary([
  SimpleTerm(term, term, unicode(term)) for term in extended_permissions_list
])

UserPermissionsVocabulary = SimpleVocabulary([
  SimpleTerm(term, term, unicode(term)) for term in user_permissions_list
])

FriendsPermissionsVocabulary = SimpleVocabulary([
  SimpleTerm(term, term, unicode(term)) for term in friends_permissions_list
])
