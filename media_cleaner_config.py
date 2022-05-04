#----------------------------------------------------------#
# Delete media type once it has been played # days ago
#   0-730500 - number of days to wait before deleting played media
#  -1 - to disable managing specified media type
# (-1 : default)
#----------------------------------------------------------#
played_age_movie=0
played_age_episode=0
played_age_audio=-1

#----------------------------------------------------------#
# Decide if media set as a favorite should be deleted
# Favoriting a series, season, or network-channel will treat all child episodes as if they are favorites
# Favoriting an artist, album-artist, or album will treat all child tracks as if they are favorites
# Similar logic applies for other media types (movies, audio books, etc...)
#  0 - ok to delete media items set as a favorite
#  1 - when single user - do not delete media items when set as a favorite; when multi-user - do not delete media item when all monitored users have set it as a favorite
#  2 - when single user - not applicable; when multi-user - do not delete media item when any monitored users have it set as a favorite
# (1 : default)
#----------------------------------------------------------#
keep_favorites_movie=1
keep_favorites_episode=1
keep_favorites_audio=1

#----------------------------------------------------------#
# Decide how whitelists with multiple users behave
#  0 - do not delete media item when ALL monitored users have the parent library whitelisted
#  1 - do not delete media item when ANY monitored users have the parent library whitelisted
# (1 : default)
#----------------------------------------------------------#
multiuser_whitelist_movie=1
multiuser_whitelist_episode=1
multiuser_whitelist_audio=1

#----------------------------------------------------------#
# User entered blacktag name; chosen during setup
#  Use a comma ',' to seperate multiple tag names
#   Ex: tagname,tag name,tag-name
#  Backslash '\' not allowed
#----------------------------------------------------------#
blacktag='deletetag'

#----------------------------------------------------------#
# User entered whitetag name; chosen during setup
#  Use a comma ',' to seperate multiple tag names
#   Ex: tagname,tag name,tag-name
#  Backslash '\' not allowed
#----------------------------------------------------------#
whitetag='keeptag'

#----------------------------------------------------------#
# Must be a boolean True or False value
#  False - Disables the ability to delete media (dry run mode)
#  True - Enable the ability to delete media
# (False : default)
#----------------------------------------------------------#
REMOVE_FILES=False

#----------------------------------------------------------#
# Advanced movie genre configurations
#     Requires 'keep_favorites_movie=1'
#----------------------------------------------------------#
#  Keep movie based on the genres
#  0 - ok to delete movie when genres are set as a favorite
#  1 - keep movie if FIRST genre listed is set as a favorite
#  2 - keep movie if ANY genre listed is set as a favorite
# (0 : default)
#----------------------------------------------------------#
keep_favorites_advanced_movie_genre=0
keep_favorites_advanced_movie_library_genre=0

#----------------------------------------------------------#
# Advanced episode genre/studio-network configurations
#     Requires 'keep_favorites_episode=1'
#----------------------------------------------------------#
#  Keep episode based on the genre(s) or studio-network(s)
#  0 - ok to delete episode when its genres or studio-networks are set as a favorite
#  1 - keep episode if FIRST genre or studio-network is set as a favorite
#  2 - keep episode if ANY genres or studio-networks are set as a favorite
# (0 : default)
#----------------------------------------------------------#
keep_favorites_advanced_episode_genre=0
keep_favorites_advanced_season_genre=0
keep_favorites_advanced_series_genre=0
keep_favorites_advanced_tv_library_genre=0
keep_favorites_advanced_tv_studio_network=0
keep_favorites_advanced_tv_studio_network_genre=0

#----------------------------------------------------------#
# Advanced track genre/artist configurations
#     Requires 'keep_favorites_audio=1'
#----------------------------------------------------------#
#  Keep track based on the genre(s) or artist(s)
#  0 - ok to delete track when its genres or artists are set as a favorite
#  1 - keep track if FIRST genre or artist is set as a favorite
#  2 - keep track if ANY genres or artists are set as a favorite
# (0 : default)
#----------------------------------------------------------#
keep_favorites_advanced_track_genre=0
keep_favorites_advanced_album_genre=0
keep_favorites_advanced_music_library_genre=0
keep_favorites_advanced_track_artist=0
keep_favorites_advanced_album_artist=0
keep_favorites_advanced_music_library_artist=0

#----------------------------------------------------------#
# Set to True to add new users or edit existing users
# Must be a boolean True or False value
#  False - Operate normally
#  True  - Enable configuration editor mode; will NOT delete media items
#           Resets REMOVE_FILES=False
# (False : default)
#----------------------------------------------------------#
UPDATE_CONFIG=False

#----------------------------------------------------------#
# CAUTION!!!   CAUTION!!!   CAUTION!!!   CAUTION!!!   CAUTION!!!
# Do NOT enable any max_age_xyz options unless you know what you are doing
# Use at your own risk; You alone are responsible for your actions
# Enabling any of these options with a low value WILL DELETE THE ENTIRE LIBRARY
# Delete media type if its creation date is x days ago; played state is ignored; value must be greater than or equal to the corresponding played_age_xyz
#   0-730500 - number of days to wait before deleting "old" media
#  -1 - to disable managing max age of specified media type
# (-1 : default)
#----------------------------------------------------------#
max_age_movie=-1
max_age_episode=-1
max_age_audio=-1

#----------------------------------------------------------#
# Decide if max age media set as a favorite should be deleted
#  0 - ok to delete max age media items set as a favorite
#  1 - do not delete max age media items when set as a favorite
# (1 : default)
#----------------------------------------------------------#
max_keep_favorites_movie=1
max_keep_favorites_episode=1
max_keep_favorites_audio=1

#------------DO NOT MODIFY BELOW---------------------------#

#----------------------------------------------------------#
# Server branding; chosen during setup
#  0 - 'emby'
#  1 - 'jellyfin'
#----------------------------------------------------------#
server_brand='emby'

#----------------------------------------------------------#
# Server URL; created during setup
#----------------------------------------------------------#
server_url='http://watch.tv/emby'

#----------------------------------------------------------#
# Authentication Key; requested from server during setup
#  Also know as an Access Token
#----------------------------------------------------------#
auth_key='0c4b78d65a3e485286890dab9c45bdcd'

#----------------------------------------------------------#
# Decide how the script will use the libraries chosen for each user
#  Only used during creation or editing of the configuration file
#  0 - blacklist - Media items in the libraries you choose will be allowed to be deleted
#  1 - whitelist - Media items in the libraries you choose will NOT be allowed to be deleted
# (blacklist : default)
#----------------------------------------------------------#
library_setup_behavior='blacklist'

#----------------------------------------------------------#
# Decide how the script will match media items to the blacklisted and whiteliested libraries
#  0 - Library Id - Media items will be matched to blacklisted and whitelisted libraries using the 'LibraryId'
#  1 - Library Path - Media items will be matched to blacklisted and whitelisted libraries using the 'Path'
#  2 - Library Network Path - Media items will be matched to blacklisted and whitelisted libraries using the 'NetworkPath'
# (byId : default)
#----------------------------------------------------------#
library_matching_behavior='byId'

#----------------------------------------------------------#
# User key(s) of monitored account(s); chosen during setup
# These are not used during runtime and only serve as a visual reminder
#----------------------------------------------------------#
user_keys='["97fbc9cf21724e4eb30bd2fb9268559d"]'

#----------------------------------------------------------#
# Blacklisted libraries with corresponding user keys(s)
# These libraries are monitored for media items to delete; chosen during setup
#----------------------------------------------------------#
user_bl_libs='[{"userid": "97fbc9cf21724e4eb30bd2fb9268559d", "4": {"libid": "4514ec850e5ad0c47b58444e17b6346c", "collectiontype": "tvshows", "path": "/media/Pharaoh/xbmc/TV", "networkpath": "smb://hieroglyph/Pharaoh/xbmc/TV"}, "2": {"libid": "f137a2dd21bbc1b99aa5c0f6bf02a805", "collectiontype": "movies", "path": "/media/Pharaoh/xbmc/Movies", "networkpath": "smb://hieroglyph/Pharaoh/xbmc/Movies"}}]'

#----------------------------------------------------------#
# Whitelisted libraries with corresponding user keys(s)
# These libraries are actively monitored for blacktagged media items to delete; chosen during setup
#----------------------------------------------------------#
user_wl_libs='[{"userid": "97fbc9cf21724e4eb30bd2fb9268559d", "0": {"libid": "48af3bb0f5988d3cd867a245b7ef32d1", "collectiontype": "audiobooks", "path": "/media/Pharaoh/xbmc/Books", "networkpath": "smb://hieroglyph/Pharaoh/xbmc/Books"}, "1": {"libid": "4e985111ed7f570b595204d82adb02f3", "collectiontype": "books", "path": "/media/Pharaoh/xbmc/Books", "networkpath": "smb://hieroglyph/Pharaoh/xbmc/Books"}, "3": {"libid": "7e64e319657a9516ec78490da03edccb", "collectiontype": "music", "path": "/media/Pharaoh/xbmc/Music/Albums", "networkpath": "smb://hieroglyph/Pharaoh/xbmc/Albums"}}]'

#----------------------------------------------------------#
# API query attempts; number of times to retry an API request
#  delay between initial attempt and the first retry is 1 second
#  The delay will double with each attempt after the first retry
#  Delay between the orginal request and retry #1 is (2^0) 1 second
#  Delay between retry #1 and retry #2 is (2^1) 2 seconds
#  Delay between retry #2 and retry #3 is (2^2) 4 seconds
#  Delay between retry #3 and retry #4 is (2^3) 8 seconds
#  Delay between retry #4 and retry #5 is (2^4) 16 seconds
#  Delay between retry #5 and retry #6 is (2^5) 32 seconds
#  ...
#  Delay between retry #15 and retry #16 is (2^15) 32768 seconds
#  0-16 - number of retry attempts
#  (4 : default)
#----------------------------------------------------------#
api_query_attempts=4

#----------------------------------------------------------#
# API query item limit; large libraries sometimes cannot return all of the media metadata items in a single API call
#  This is especially true when using the max_age_xyz options; which requires every item of the specified media type send its metadata
#  1-10000 - number of media metadata items the server will return for each API call for media item metadata; ALL queried items will be processed regardless of this value
#  (50 : default)
#----------------------------------------------------------#
api_query_item_limit=50

#----------------------------------------------------------#
# Must be a boolean True or False value
# False - Debug messages disabled
# True - Debug messages enabled
# (False : default)
#----------------------------------------------------------#
DEBUG=False
