# Version 2.1.0 And Later Are Not Backwards Compatible
* media_cleaner.py [Version 2.1.0 updates and changes](https://github.com/terrelsa13/media_cleaner/issues/23#issue-1260958344)
* Previous versions of the config are not compatible with this latest version of the script.
* If you are running an unversioned script or a version before version 2.1.0 you will need to do the following:
   - Renaming the current media_cleaner folder
   - Create a new media_cleaner folder
   - Download the updated version of the script into the new folder
   - [Manually run the script](https://github.com/terrelsa13/media_cleaner#first-run-debian-ubuntu-and-linux-mint) the first time to allow it to rebuild the config file
   - Make any manual changes to the config that are needed
   - Verify script runs as desired
   - After running as desired set `REMOVE_FILES=True`
   - If Linux set script to [run in crontab](https://github.com/terrelsa13/media_cleaner/edit/master/README.md#schedule-to-run-using-crontab-debian-ubuntu-and-linux-mint)
   - Delete the renamed folder from the first step
   - Enjoy not having to manually delete episodes, movies, audio tracks, and audio books
# Script
## media_cleaner.py
This script will go through played, favorited, and/or tagged movies, tv episodes, audio, and audiobooks for the specified user(s) and their configured libraries; deleting any media items played past the configured number of days.

# Configuration
## media_cleaner_config.py
The first time you run the script it will attempt to create the config file by asking a handful of questions.
## media_cleaner_config_defaults.py
_**Optional:**_ Before running the script for the first time; edit ```media_cleaner_config_defaults.py``` to customize the default values used to create ```media_cleaner_config.py```.
## Contents Of The Configuration File

#### Media will be deleted once it has been played the configured number of days ago:
```python
#----------------------------------------------------------#
# Delete media type once it has been played # days ago
#   0-730500 - number of days to wait before deleting played media
#  -1 - to disable managing specified media type
# (-1 : default)
#----------------------------------------------------------#
played_age_movie=-1
played_age_episode=-1
played_age_audio=-1
played_age_audiobook=-1
```
#### When enabled, media will not be deleted if it is marked as a favorite:
```python
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
keep_favorites_audiobook=1
```
#### Option for determining if a media item should be deleted or kept based on other users whitelisted libraries:
```python
#----------------------------------------------------------#
# Decide how whitelists with multiple users behave
#  0 - do not delete media item when ALL monitored users have the parent library whitelisted
#  1 - do not delete media item when ANY monitored users have the parent library whitelisted
# (1 : default)
#----------------------------------------------------------#
multiuser_whitelist_movie=1
multiuser_whitelist_episode=1
multiuser_whitelist_audio=1
multiuser_whitelist_audiobook=1
```
#### Blacktag a media item to be deleted after it is watched:
```python
#----------------------------------------------------------#
# User entered blacktag name; chosen during setup
#  Use a comma ',' to seperate multiple tag names
#   Ex: tagname,tag name,tag-name
#  Backslash '\' not allowed
#----------------------------------------------------------#
blacktag='black_tagname,black_tag name,black_tag-name'
```
#### When enabled, blacktagged media will not be deleted until ALL users have watched it:
```python
#----------------------------------------------------------#
# Decide when blacktagged media items are deleted
#  0 - ok to delete blacktagged media item after ANY monitored user has watched it
#  1 - ok to delete blacktagged media item after ALL monitored users have watched it
# (0 : default)
#----------------------------------------------------------#
delete_blacktagged_movie=0
delete_blacktagged_episode=0
delete_blacktagged_audio=0
delete_blacktagged_audiobook=0
```
#### Whitetag a media item to be kept after it is watched:
```python
#----------------------------------------------------------#
# User entered whitetag name; chosen during setup
#  Use a comma ',' to seperate multiple tag names
#   Ex: tagname,tag name,tag-name
#  Backslash '\' not allowed
#----------------------------------------------------------#
whitetag='white_tagname,white_tag name,white_tag-name'
```
#### Deleting media items is disabled by default:
```python
#----------------------------------------------------------#
# Must be a boolean True or False value
#  False - Disables the ability to delete media (dry run mode)
#  True - Enable the ability to delete media
# (False : default)
#----------------------------------------------------------#
REMOVE_FILES=False
```
#### At least this many episodes will reamain in each tv series:
```python
#----------------------------------------------------------#
# Decide the minimum number of episodes to remain in all tv series'
# Keeping one or more epsiodes for each series allows the "Next Up"
#  functionality to notify user(s) when a new episode for a series
#  is ready to be watched
#  0 - Episodes will be deleted as they are watched
#  1-730500 - All but the latest selected number of episodes will be deleted as they are watched
# (0 : default)
#----------------------------------------------------------#
minimum_number_episodes=0
```
#### Keep movie if genre favorited:
```python
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
```
#### Keep episode if genre or studio-network favorited:
```python
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
```
#### Keep track if genre or artist favorited:
```python
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
```
#### Keep audio book track if genre or author favorited:
```python
#----------------------------------------------------------#
# Advanced audio book track genre/author configurations
#     Requires 'keep_favorites_audiobook=1'
#----------------------------------------------------------#
#  Keep audio book track based on the genres or authors
#  0 - ok to delete audio book track when its genres or authors are set as a favorite
#  1 - keep audio book track if FIRST genre or author is set as a favorite
#  2 - keep audio book track if ANY genres or authors are set as a favorite
# (0 : default)
#----------------------------------------------------------#
keep_favorites_advanced_audio_book_track_genre=0
keep_favorites_advanced_audio_book_genre=0
keep_favorites_advanced_audio_book_library_genre=0
keep_favorites_advanced_audio_book_track_author=0
keep_favorites_advanced_audio_book_author=0
```
#### Edit user to library assocations using current config
```python
#----------------------------------------------------------#
# Set to True to add new users or edit existing users
# Must be a boolean True or False value
#  False - Operate normally
#  True  - Enable configuration editor mode; will NOT delete media items
#           Resets to dry run mode (REMOVE_FILES=False)
# (False : default)
#----------------------------------------------------------#
UPDATE_CONFIG=False
```
#### !!!CAUTION!!!   READ max_age_* DESCRIPTION VERY CAREFULLY   !!!CAUTION!!!
```python
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
max_age_audiobook=-1
```
#### !!!CAUTION!!!   READ max_keep_favorites_* DESCRIPTION VERY CAREFULLY   !!!CAUTION!!!
```python
#----------------------------------------------------------#
# Decide if max age media set as a favorite should be deleted
#  0 - ok to delete max age media items set as a favorite
#  1 - do not delete max age media items when set as a favorite
# (1 : default)
#----------------------------------------------------------#
max_keep_favorites_movie=1
max_keep_favorites_episode=1
max_keep_favorites_audio=1
max_keep_favorites_audiobook=1
```

### Created first time the script runs; Do **_NOT_** edit or modify these:
#### Needed for differences between Emby and Jellyfin?
```python
#------------DO NOT MODIFY BELOW---------------------------#

#----------------------------------------------------------#
# Server branding; chosen during setup
#  0 - 'emby'
#  1 - 'jellyfin'
#----------------------------------------------------------#
server_brand='serverbrand'
```
#### Full URL of media server
```python
#----------------------------------------------------------#
# Server URL; created during setup
#----------------------------------------------------------#
server_url='http://localhost.abc:8096/basename'
```
#### Server authentication key
```python
#----------------------------------------------------------#
# Authentication Key; requested from server during setup
#  Used for API queries sent to the server
#  Also know as an Access Token
#----------------------------------------------------------#
auth_key='0123456789abcdef0123456789abcdef'
```
#### How were libraries selected during setup?
```python
#----------------------------------------------------------#
# Decide how the script will use the libraries chosen for each user
#  Only used during creation or editing of the configuration file
#  0 - blacklist - Chosen libraries will be blacklisted
#                  All other libraries will be whitelisted
#  1 - whitelist - Chosen libraries will be whitelisted
#                  All other libraries will be blacklisted
# (blacklist : default)
#----------------------------------------------------------#
script_behavior='abclist'
```
#### How will media items be matched to their respective libraries?
```python
#----------------------------------------------------------#
# Decide how the script will match media items to the blacklisted and whiteliested libraries
#  0 - byId - Media items will be matched to libraries using 'LibraryIds'
#  1 - byPath - Media items will be matched to libraries using 'Paths'
#  2 - byNetworkPath - Media items will be matched to libraries using 'NetworkPaths'
# (byId : default)
#----------------------------------------------------------#
library_matching_behavior='byAbc'
```
#### UserId for each monitored user
```python
#----------------------------------------------------------#
# User name(s) and user key(s) of monitored account(s); chosen during setup
# The order of the names:keys here must match the order of the names:keys
#  in user_bl_libs and user_wl_libs
#----------------------------------------------------------#
user_keys='["user1:abcdef0123456789abcdef0123456789", "user2:fedcba9876543210fedcba9876543210", "user3:9876543210fedcba9876543210fedcba", "etc..."]'
```
#### Blacklisted library information
```python
#----------------------------------------------------------#
# Blacklisted libraries with corresponding user keys(s)
# These libraries are typically searched for media items to delete
# Chosen during setup
#----------------------------------------------------------#
user_bl_libs='[{"userid": "abcdef0123456789abcdef0123456789", "#": {"libid": "00112233445566778899aabbccddeeff", "collectiontype": "abc", "networkpath": "smb://some/netpath/0", "path": "/some/path/0"}, "#": {"libid": "aabbccddeeff00112233445566778899", "collectiontype": "def", "networkpath": "smb://some/netpath/1", "path": "/some/path/1"}}, {"etc...": "etc...", "#": {"etc...":"etc..."}}]'
```
#### Whitelisted library information
```python
#----------------------------------------------------------#
# Whitelisted libraries with corresponding user keys(s)
# These libraries are typically not searched for media items to delete
# Chosen during setup
#----------------------------------------------------------#
user_wl_libs='[{"userid": "abcdef0123456789abcdef0123456789", "#": {"libid": "ffeeddccbbaa99887766554433221100", "collectiontype": "uvw", "networkpath": "smb://some/netpath/2", "path": "/some/path/2"}, "#": {"libid": "998877665544332211ffeeddccbbaa", "collectiontype": "xyz", "networkpath": "smb://some/netpath/3", "path": "/some/path/3"}}, {"etc...": "etc...", "#": {"etc...":"etc..."}}]'
```
#### Number of times to send an API query before giving up
```python
#----------------------------------------------------------#
# API query attempts
# Number of times to retry an API request
#  Delay between initial attempt and the first retry is 1 second
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
```
#### Throttle how aggressively the script sends queries
```python
#----------------------------------------------------------#
# API query item limit
# To keep the server running smoothly we do not want it to return a
#  large amount of metadata from a single API query
# If the server lags or bogs down when this script runs try lowering
#  this value to allow the server to return smaller amounts of data
# ALL media items and their metadata are processed regardless of this value
#  1-10000 - maximum number of media items the server will return for each API query
#  (50 : default)
#----------------------------------------------------------#
api_query_item_limit=50
```
#### DEBUG
```python
#----------------------------------------------------------#
# Must be a boolean True or False value
# False - Debug messages disabled
# True - Debug messages enabled
# (False : default)
#----------------------------------------------------------#
DEBUG=False
```
#
# Requirements
* Linux or Windows
   - Mac - I do not have a Mac to confirm
   - If someone has confirmed this works on Mac, let me know and I will update this.
* Python 3.10
   - Older versions of python 3.x will likely work; but are not supported
   - Python 2.x or earlier are not supported and will not work
* python-dateutil \***must** be installed\*
* media_cleaner_config_defaults.py **\*new\***
* Emby/Jellyfin need to have permissions on Linux machines to delete media items (read from [this post](https://github.com/clara-j/media_cleaner/issues/2#issuecomment-547319398) down)

# Delete Or Keep Priorities Of A Played Media Item

At least one monitored user must have played the media item before it will be considered for deletion.<sup>1</sup>

1. **Favorites & Whitetags** (Highest Priority)
   - *media item will be kept*
      - Blacktags ignored
      - Whitelists ignored
      - Blacklists ignored
2. **Blacktags**
   - *media item will be deleted*
      - Whitelists ignored
      - Blacklists ignored
3. **Whitelists**
   - *media item will be kept*
      - Blacklists ignored
4. **Blacklists** (Lowest priority)
   - *media item will be deleted*

<sup>1</sup> If max_age_* is enabled the media item's 'Creation Date' is used and its 'Played State' is ignored.

# Blacklisting vs Whitelisting
* [Explaination and examples.](https://github.com/clara-j/media_cleaner/issues/32#issuecomment-1022755271)

# Blacktagging vs Whitetagging
* [Explaination and examples.](https://github.com/terrelsa13/media_cleaner/issues/16#issue-1205993797)

# minimum_number_episodes=#
* [Explaination and examples.](https://github.com/terrelsa13/media_cleaner/issues/21#issue-1258905586)

# Library Matching By Id, By Path, or By Network Path
* [Explaination and examples.](https://github.com/terrelsa13/media_cleaner/issues/18#issue-1217953189)

# First Run (Debian, Ubuntu, and Linux Mint)
* Install Python version mentioned in the 'Requirements' section above
   - If this version of Python is not installed do NOT overwrite the OS default Python version
   - Instead use the link below to create an alternate install of Python
      - [Python 3.7.x example](https://tecadmin.net/install-python-3-7-on-ubuntu-linuxmint/)
* **\*OPTIONAL\*** Update the media_cleaner_config_defaults.py file with desired default values
   - $```nano /path/to/media_cleaner_config_defaults.py```
* Make the script executable
   - $```chmod +x /path/to/media_cleaner.py```
* Run the script
   - $```/path/to/python3.x /path/to/media_cleaner.py```
* First time the script is run, it will walk through building the media_cleaner_config.py file
* The below python error may be generated if the python-dateutil module is not installed
   - ```ModuleNotFoundError: No module named 'dateutil' python-dateutil```
* The python-dateutil module can be installed with the following commands:
   - $```sudo apt-get update```
   - $```sudo apt-get upgrade -y```
   - $```sudo apt-get install python3-pip -y```
   - $```pip3 install -U pip```
   - $```pip3 install python-dateutil```

# First Run (Other Operating Systems)
* Please consult your favorite search engine

# Schedule To Run Using Crontab (Debian, Ubuntu, and Linux Mint)
* Below cron entry runs script everyday at 00:00hrs (aka 12AM)
   - $```0 0 * * * /usr/local/bin/python3.10 /opt/media_cleaner/media_cleaner.py```
* Below cron entry runs script every Monday at 01:23hrs (aka 1:23AM) and saves the output to a file called media_cleaner.log in the /var/log/ directory
   - $```23 1 * * 1 /usr/local/bin/python3.10 /opt/media_cleaner/media_cleaner.py > /var/log/media_cleaner.log 2>&1```

# Schedule To Run (Other Operating Systems)
* Please consult your favorite search engine

# Donation
If you find this script useful and would like to show support, please consider the option below.

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/donate?hosted_button_id=4CFFHMJV3H4M2)
