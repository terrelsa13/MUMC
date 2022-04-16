

# Script
## media_cleaner.py
This script will go through all played movies, tv episodes, audio, and audiobooks for the specified user(s) and their configured libraries; deleting any media played past the configured number of days.

# Configuration
## media_cleaner_config.py
The first time you run the script it will attempt to create the config file by asking a handful of questions.
## media_cleaner_config_defaults.py
Customize your default values before running for the script the first time.
## Configuration Contents

#### Media will be deleted once it has been played the configured number of days ago:
```python
#----------------------------------------------------------#
# Delete media type once it has been played # days ago
#   0-730500 - number of days to wait before deleting played media
#  -1 - to disable managing specified media type
# (-1 : default)
#----------------------------------------------------------#
not_played_age_movie=-1
not_played_age_episode=-1
not_played_age_audio=-1
not_played_age_audiobook=-1
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
#### Additional options for determining if a media item should be considered marked as a favorite based on specified metadata item:
```python
#----------------------------------------------------------#
# Decide how whitelists with multiple users behave
#  0 - do not delete media item when ALL monitored users have the parent library whitelisted
#  1 - do not delete media item when ANY monitored users have the parent library whitelisted
# (1 : default)
#----------------------------------------------------------#
multiuser_whitelist_movie=1
multiuser_whitelist_episode=1
multiuser_whitelist_video=1
multiuser_whitelist_audio=1
```
#### Blacktag a watched media item to be deleted:
```python
#----------------------------------------------------------#
# User entered blacktag name; chosen during setup
#  Use comma ',' to seperate multiple tag names
#   Ex: tagname,tag name,tag-name
#  Backslash '\' not allowed
#----------------------------------------------------------#
blacktag='tagname,tag name,tag-name'
```
#### Whitetag a watched media item to be kept:
```python
#----------------------------------------------------------#
# User entered whitetag name; chosen during setup
#  Use comma ',' to seperate multiple tag names
#   Ex: tagname,tag name,tag-name
#  Backslash '\' not allowed
#----------------------------------------------------------#
whitetag='tagname,tag name,tag-name'
```
#### Deleting media items is disabled by default:
```python
#----------------------------------------------------------#
#  0 - Disable the ability to delete media (dry run mode)
#  1 - Enable the ability to delete media
# (0 : default)
#----------------------------------------------------------#
remove_files=0
```
### When monitoring multiple users whitelisted libraries will be treated accordingly:
#### Keep movie if genre favorited:
```python
#----------------------------------------------------------#
# Advanced movie genre configurations
#     Requires 'keep_favorites_movie=1'
#----------------------------------------------------------#
#  Keep movie based on the movie's genre
#  0 - ok to delete movie when its genres are set as a favorite
#  1 - keep movie if FIRST genre listed in the movie's metadata is set as a favorite
#  2 - keep movie if ANY genre listed in the movie's metadata is set as a favorite
# (1 : default)
#----------------------------------------------------------#
keep_favorites_advanced_movie_genre=0
```
#### Keep movie if library's genre favorited:
```python
#----------------------------------------------------------#
#  Keep movie based on the movie library's genre
#  0 - ok to delete movie when its movie-library genres are set as a favorite
#  1 - keep movie if FIRST genre listed in the movie-library's metadata is set as a favorite
#  2 - keep movie if ANY genre listed in the movie-library's metadata is set as a favorite
# (1 : default)
#----------------------------------------------------------#
keep_favorites_advanced_movie_library_genre=0
```
#### Keep episode if genre favorited:
```python
#----------------------------------------------------------#
# Advanced episode genre configurations
#     Requires 'keep_favorites_episode=1'
#----------------------------------------------------------#
#  Keep episode based on the episode's genre
#  0 - ok to delete episode when its genres are set as a favorite
#  1 - keep episode if FIRST genre listed in the episode's metadata is set as a favorite
#  2 - keep episode if ANY genre listed in the episode's metadata is set as a favorite
# (1 : default)
#----------------------------------------------------------#
keep_favorites_advanced_episode_genre=0
```
#### Keep episode if season's genre favorited:
```python
#----------------------------------------------------------#
#  Keep episode based on the season's genre
#  0 - ok to delete episode when its season genres are set as a favorite
#  1 - keep episode if FIRST genre listed in the season's metadata is set as a favorite
#  2 - keep episode if ANY genre listed in the season's metadata is set as a favorite
# (1 : default)
#----------------------------------------------------------#
keep_favorites_advanced_season_genre=0
```
#### Keep episode if series' genre favorited:
```python
#----------------------------------------------------------#
#  Keep episode based on the series' genre
#  0 - ok to delete episode when its series genres are set as a favorite
#  1 - keep episode if FIRST genre listed in the series' metadata is set as a favorite
#  2 - keep episode if ANY genre listed in the series' metadata is set as a favorite
# (1 : default)
#----------------------------------------------------------#
keep_favorites_advanced_series_genre=0
```
#### Keep episode if library's genre favorited:
```python
#----------------------------------------------------------#
#  Keep episode based on the tv-library's genre
#  0 - ok to delete episode when its tv-library genres are set as a favorite
#  1 - keep episode if FIRST genre listed in the tv-library's metadata is set as a favorite
#  2 - keep episode if ANY genre listed in the tv-library's metadata is set as a favorite
# (1 : default)
#----------------------------------------------------------#
keep_favorites_advanced_tv_library_genre=0
```
#### Keep episode if studio network favorited:
```python
#----------------------------------------------------------#
#  Keep episode based on the studio-network
#  0 - ok to delete episode when its series' studio-networks are set as a favorite
#  1 - keep episode if FIRST studio-network listed in the series' metadata is set as a favorite
#  2 - keep episode if ANY studio-network listed in the series' metadata is set as a favorite
# (1 : default)
#----------------------------------------------------------#
keep_favorites_advanced_tv_studio_network=0
```
#### Keep episode if studio network's genre favorited:
```python
#----------------------------------------------------------#
#  Keep episode based on the studio-network's genre
#  0 - ok to delete episode when its studio-network genres are set as a favorite
#  1 - keep episode if FIRST genre listed in the studio-network's metadata is set as a favorite
#  2 - keep episode if ANY genre listed in the studio-network's metadata is set as a favorite
# (1 : default)
#----------------------------------------------------------#
keep_favorites_advanced_tv_studio_network_genre=0
```
#### Keep track if genre favorited:
```python
#----------------------------------------------------------#
# Advanced track genre configurations
#     Requires 'keep_favorites_audio=1'
#----------------------------------------------------------#
#  Keep track based on the track's genre
#  0 - ok to delete track when its genres are set as a favorite
#  1 - keep track if FIRST genre listed in the track's metadata is set as a favorite
#  2 - keep track if ANY genre listed in the track's metadata is set as a favorite
# (1 : default)
#----------------------------------------------------------#
keep_favorites_advanced_track_genre=0
```
#### Keep track if album's genre favorited:
```python
#----------------------------------------------------------#
#  Keep track based on the album's genre
#  0 - ok to delete track when its album's genres are set as a favorite
#  1 - keep track if FIRST genre listed in the album's metadata is set as a favorite
#  2 - keep track if ANY genre listed in the album's metadata is set as a favorite
# (1 : default)
#----------------------------------------------------------#
keep_favorites_advanced_album_genre=0
```
#### Keep track if library's genre favorited:
```python
#----------------------------------------------------------#
#  Keep track based on the music-library's genre
#  0 - ok to delete track when its music-library genres are set as a favorite
#  1 - keep track if FIRST genre listed in the music-library's metadata is set as a favorite
#  2 - keep track if ANY genre listed in the music-library's metadata is set as a favorite
# (1 : default)
#----------------------------------------------------------#
keep_favorites_advanced_music_library_genre=0
```
#### Keep track if artist favorited:
```python
#----------------------------------------------------------#
# Advanced track artist configurations
#     Requires 'keep_favorites_audio=1'
#----------------------------------------------------------#
#  Keep track based on the track's artist
#  0 - ok to delete track when its artists are set as a favorite
#  1 - keep track if FIRST artist listed in the track's metadata is set as a favorite
#  2 - keep track if ANY artist listed in the track's metadata is set as a favorite
# (1 : default)
#----------------------------------------------------------#
keep_favorites_advanced_track_artist=0
```
#### Keep track if album artist favorited:
```python
#----------------------------------------------------------#
#  Keep track based on the album's artist
#  0 - ok to delete track when its album's artists are set as a favorite
#  1 - keep track if FIRST artist listed in the album's metadata is set as a favorite
#  2 - keep track if ANY artist listed in the album's metadata is set as a favorite
# (1 : default)
#----------------------------------------------------------#
keep_favorites_advanced_album_artist=1
```
#### Keep track if library artist favorited:
```python
#----------------------------------------------------------#
#  Keep track based on the music-library's artist
#  0 - ok to delete track when its music-library artists are set as a favorite
#  1 - keep track if FIRST artist listed in the music-library's metadata is set as a favorite
#  2 - keep track if ANY artist listed in the music-library's metadata is set as a favorite
# (1 : default)
#----------------------------------------------------------#
keep_favorites_advanced_music_library_artist=0
```
#### Edit user to library assocations using current config
```python
#----------------------------------------------------------#
# Used to add new users to the existing media_cleaner_config.py file; must be string with UPPERCASE letters
# Does not show existing users in the choice list; but existing users can be updated if you know their position
#  FALSE - Operate as configured
#  TRUE  - Allow adding new users to existing config; will NOT delete media items
# (FALSE : default)
#----------------------------------------------------------#
UPDATE_CONFIG='FALSE'
```
#### !!!CAUTION!!!   READ max_age_* DESCRIPTION VERY CAREFULLY   !!!CAUTION!!!
```python
#----------------------------------------------------------#
# CAUTION!!!   CAUTION!!!   CAUTION!!!   CAUTION!!!   CAUTION!!!
# Do NOT enable any max_age_xyz options unless you know what you are doing
# Use at your own risk; You alone are responsible for your actions
# Enabling any of these options with a low value WILL DELETE THE ENTIRE LIBRARY
# Delete media type if its creation date is x days ago; played state is ignored; value must be greater than or equal to the corresponding not_played_age_xyz
#   0-730500 - number of days to wait before deleting "old" media
#  -1 - to disable managing max age of specified media type
# (-1 : default)
#----------------------------------------------------------#
max_age_movie=-1
max_age_episode=-1
max_age_video=-1
max_age_audio=-1
```
#### CAUTION!!!   READ max_age_* DESCRIPTION VERY CAREFULLY   CAUTION!!!
```python
#----------------------------------------------------------#
# Decide if max age media set as a favorite should be deleted
#  0 - ok to delete max age media items set as a favorite
#  1 - do not delete max age media items when set as a favorite
# (1 : default)
#----------------------------------------------------------#
max_keep_favorites_movie=1
max_keep_favorites_episode=1
max_keep_favorites_video=1
max_keep_favorites_audio=1
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
#### Media server's admin username
```python
#----------------------------------------------------------#
# Admin username; entered during setup
#----------------------------------------------------------#
admin_username='username'
```
#### Server authentication key
```python
#----------------------------------------------------------#
# Authentication Key; requested from server during setup
#  Also know as an Access Token
#----------------------------------------------------------#
auth_key='0123456789abcdef0123456789abcdef'
```
#### How were libraries selected during setup?
```python
#----------------------------------------------------------#
# Decide how the script will use the libraries chosen for each user.
#  0 - blacklist - Media items in the libraries you choose will be allowed to be deleted.
#  1 - whitelist - Media items in the libraries you choose will NOT be allowed to be deleted.
# (blacklist : default)
#----------------------------------------------------------#
script_behavior='abclist'
```
#### UserId for each monitored user
```python
#----------------------------------------------------------#
# User key(s) of monitored account(s); chosen during setup
#----------------------------------------------------------#
user_keys='["abcdef0123456789abcdef0123456789", "fedcba9876543210fedcba9876543210", "9876543210fedcba9876543210fedcba", "etc..."]'
```
#### Blacklisted library information
```python
#----------------------------------------------------------#"
# Blacklisted libraries with corresponding user keys(s)"
# These libraries are actively monitored for media items to delete; chosen during setup"
#----------------------------------------------------------#"
user_bl_libs='[{"userid": "abcdef0123456789abcdef0123456789", "#": {"libid": "00112233445566778899aabbccddeeff", "collectiontype": "abc", "networkpath": "smb://some/netpath/0", "path": "/some/path/0"}, "#": {"libid": "aabbccddeeff00112233445566778899", "collectiontype": "def", "networkpath": "smb://some/netpath/1", "path": "/some/path/1"}}, {"etc...": "etc...", "#": {"etc...":"etc..."}}]'
```
#### Whitelisted library information
```python
#----------------------------------------------------------#"
# Whitelisted libraries with corresponding user keys(s)"
# These libraries are NOT actively monitored for media items to delete; chosen during setup"
#----------------------------------------------------------#"
user_wl_libs='[{"userid": "abcdef0123456789abcdef0123456789", "#": {"libid": "ffeeddccbbaa99887766554433221100", "collectiontype": "uvw", "networkpath": "smb://some/netpath/2", "path": "/some/path/2"}, "#": {"libid": "998877665544332211ffeeddccbbaa", "collectiontype": "xyz", "networkpath": "smb://some/netpath/3", "path": "/some/path/3"}}, {"etc...": "etc...", "#": {"etc...":"etc..."}}]'
```
#### Number of times to send an API query before giving up
```python
#----------------------------------------------------------#
# API request attempts; number of times to retry an API request
#  delay between initial attempt and the first retry is 1 second
#  The delay will double with each attempt after the first retry
#  Delay between the orginal request and retry 1 is (2^0) 1 second
#  Delay between retry 1 and retry 2 is (2^1) 2 seconds
#  Delay between retry 2 and retry 3 is (2^2) 4 seconds
#  Delay between retry 3 and retry 4 is (2^3) 8 seconds
#  Delay between retry 4 and retry 5 is (2^4) 16 seconds
#  Delay between retry 5 and retry 6 is (2^5) 32 seconds
#  ...
#  Delay between retry 15 and retry 16 is (2^15) 32768 seconds
#  0-16 - number of retry attempts
#  (4 : default)
#----------------------------------------------------------#
api_request_attempts=4
```
#### Throttle how aggressively the script sends queries
```python
#----------------------------------------------------------#
# API return limit; large libraries sometimes cannot return all of the media metadata items in a single API call
#  This is especially true when using the max_age_xyz or return_not_played options; both require every item of the specified media type send its metadata
#  1-10000 - number of media metadata items the server will return for each API call for media item metadata; ALL queried items will be processed regardless of this value
#  (100 : default)
#----------------------------------------------------------##
api_return_limit=100
```
#### DEBUG
```python
#----------------------------------------------------------#
# 0 - Debug messages disabled
# 1 - Debug messages enabled
# (0 : default)
#----------------------------------------------------------#
DEBUG=0
```

# Usage
Make ```media_cleaner.py``` executable and run ```python3.x /path/to/media_cleaner.py```.  If no ```media_cleaner_conifg.py``` file is found the script will query for the information needed to create one.  After the config is created, run the script again to view files that will be deleted.

# Requirements
* Linux or Windows
* Mac (probably works but do not have a Mac to confirm)
* python3.x
* python-dateutil
* Emby/Jellyfin need to have permissions to delete media items (read from [this post](https://github.com/clara-j/media_cleaner/issues/2#issuecomment-547319398) down)

# Blacklisting vs Whitelisting
* [Explaination and examples.](https://github.com/clara-j/media_cleaner/issues/32#issuecomment-1022755271)

# Blacktagging vs Whitetagging
* [Explaination and examples. (WIP)]()

# First Run
* $```/path/to/python3.x /path/to/media_cleaner.py```
* You may get the below python error if the python-dateutil module is not installed
   - ModuleNotFoundError: No module named 'dateutil' python-dateutil
* For Debian/Ubuntu/Linux Mint type systems you can install the python-dateutil module with the following commands:
   - $```sudo apt-get update```
   - $```sudo apt-get upgrade -y```
   - $```sudo apt-get install python3-pip -y```
   - $```sudo pip3 install -U pip```
   - $```sudo pip3 install python-dateutil```
* For other operating systems
   - Please consult Google

# Scheduled Run Using Crontab
* Below cron entry runs script everyday at 00:00hrs (aka 12AM)
   - $```0 0 * * * /usr/local/bin/python3.8 /opt/media_cleaner/media_cleaner.py```
* Below cron entry runs script every Monday at 01:23hrs (aka 1:23AM) and saves the output to a file called media_cleaner.log in the /var/log/ directory
   - $```23 1 * * 1 /usr/local/bin/python3.8 /opt/media_cleaner/media_cleaner.py > /var/log/media_cleaner.log 2>&1```


# Donation
If you find this script useful and you would like to show your support, please consider the option below.

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/donate?hosted_button_id=4CFFHMJV3H4M2)
