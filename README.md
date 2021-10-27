# Script
## media_cleaner.py
This script will go through all played movies, tv episodes, videos, trailers, and audio for the specified user(s); deleting any media past the specified played age cut off.

# Configuration
## media_cleaner_config.py
The first time you run the script it will attempt to create the config file by asking a handful of questions.

## Configuration Contents
#### Media will be deleted once it has been played the configured number of days ago:
```python
#----------------------------------------------------------#
# Delete media type once it has been played x days ago
#   0-365000000 - number of days to wait before deleting played media
#  -1 : to disable managing specified media type
# (-1 : default)
#----------------------------------------------------------#
not_played_age_movie=-1
not_played_age_episode=-1
not_played_age_video=-1
not_played_age_trailer=-1
not_played_age_audio=-1
```
#### When enabled, media will not be deleted if it is marked as a favorite:
```python
#----------------------------------------------------------#
# Decide if media set as a favorite should be deleted
# Favoriting a series, season, or network-channel will treat all child episodes as if they are favorites
# Favoriting an artist, album-artist, or album will treat all child tracks as if they are favorites
# Similar logic applies for other media types (movies, trailers, etc...)
#  0 : ok to delete media items set as a favorite
#  1 : when single user - do not delete media items when set as a favorite; when multi-user - do not delete media item when all monitored users have set it as a favorite
#  2 : when single user - not applicable; when multi-user - do not delete media item when any monitored users have it set as a favorite
# (1 : default)
#----------------------------------------------------------#
keep_favorites_movie=1
keep_favorites_episode=1
keep_favorites_video=1
keep_favorites_trailer=1
keep_favorites_audio=1
```
#### Additional options for determining if a media item should be considered marked as a favorite based on specified metadata item:
```python
#----------------------------------------------------------#
# Advanced favorites configuration bitmask
#     Requires 'keep_favorites_*=1'
#  xxxxxxxA - keep_favorites_audio must be enabled; keep audio tracks based on if the FIRST artist listed in the track's 'artist' metadata is favorited
#  xxxxxxBx - keep_favorites_audio must be enabled; keep audio tracks based on if the FIRST artist listed in the tracks's 'album artist' metadata is favorited
#  xxxxxCxx - keep_favorites_audio must be enabled; keep audio tracks based on if the FIRST genre listed in the tracks's metadata is favorited
#  xxxxDxxx - keep_favorites_audio must be enabled; keep audio tracks based on if the FIRST genre listed in the album's metadata is favorited
#  xxxExxxx - keep_favorites_episode must be enabled; keep episode based on if the FIRST genre listed in the series' metadata is favorited
#  xxFxxxxx - keep_favorites_movie must be enabled; keep movie based on if the FIRST genre listed in the movie's metadata is favorited
#  xGxxxxxx - reserved...
#  Hxxxxxxx - reserved...
#  0 bit - disabled
#  1 bit - enabled
# (00000001 - default)
#----------------------------------------------------------#
keep_favorites_advanced='00000001'
```
#### Dependent on the above "advanced options", determines if only the first metadata item should be considered or all metadata items should be considered:
```python
#----------------------------------------------------------#
# Advanced favorites any configuration bitmask
#     Requires matching bit in 'keep_favorites_advanced' bitmask is enabled
#  xxxxxxxa - xxxxxxxA must be enabled; will use ANY artists listed in the track's 'artist' metadata
#  xxxxxxbx - xxxxxxBx must be enabled; will use ANY artists listed in the track's 'album artist' metadata
#  xxxxxcxx - xxxxxCxx must be enabled; will use ANY genres listed in the track's metadata
#  xxxxdxxx - xxxxDxxx must be enabled; will use ANY genres listed in the album's metadata
#  xxxexxxx - xxxExxxx must be enabled; will use ANY genres listed in the series' metadata
#  xxfxxxxx - xxFxxxxx must be enabled; will use ANY genres listed in the movie's metadata
#  xgxxxxxx - reserved...
#  hxxxxxxx - reserved...
#  0 bit - disabled
#  1 bit - enabled
# (00000000 - default)
#----------------------------------------------------------#
keep_favorites_advanced_any='00000000'
```
#### When monitoring multiple users whitelisted libraries will be treated accordingly:
```python
#----------------------------------------------------------#
# Decide how whitelists with multiple users behave
#  0 : when multi-user - do not delete media item when ALL monitored users have the parent library whitelisted
#  1 : when multi-user - do not delete media item when ANY monitored users have the parent library whitelisted
# (1 : default)
#----------------------------------------------------------#
multiuser_whitelist_movie=1
multiuser_whitelist_episode=1
multiuser_whitelist_video=1
multiuser_whitelist_trailer=1
multiuser_whitelist_audio=1
```
#### Allows the script to be run without deleting media (i.e. for testing and setup); Set to 1 when ready for "production":
```python
#----------------------------------------------------------#
# 0 - Disable the ability to delete media (dry run mode)
# 1 - Enable the ability to delete media
# (0 - default)
#----------------------------------------------------------#
remove_files=0
```
#### Allows adding new users and their associated libraries to the existing config without deleting it; Set to 'FALSE' when ready for "production":
```python
#----------------------------------------------------------#
# Used to add new users to the existing media_cleaner_config.py file; must be string with UPPERCASE letters
# Does not allow updating libraries for existing users
#  FALSE - Operate as configured
#  TRUE  - Allow adding new users to existing config; will NOT delete media items
# (FALSE - default)
#----------------------------------------------------------#
UPDATE_CONFIG='FALSE'
```
#### When enabled, media items will be deleted based on DateCreated; played state will be ignored:
```python
#----------------------------------------------------------#
# CAUTION!!!   CAUTION!!!   CAUTION!!!   CAUTION!!!   CAUTION!!!
# Do NOT enable any max_age_xyz options unless you know what you are doing
# Use at your own risk; You alone are responsible for your actions
# Enabling any of these options with a low value WILL DELETE THE ENTIRE LIBRARY
# Delete media type if its creation date is x days ago; played state is ignored; value must be greater than or equal to the corresponding not_played_age_xyz
#   0-365000000 - number of days to wait before deleting "old" media
#  -1 : to disable managing max age of specified media type
# (-1 : default)
#----------------------------------------------------------#
max_age_movie=-1
max_age_episode=-1
max_age_video=-1
max_age_trailer=-1
max_age_audio=-1
```
#### When enabled, favorited media items will not be deleted using the corresponding max_age_xyz:
```python
#----------------------------------------------------------#
# Decide if max age media set as a favorite should be deleted
#  0 : ok to delete max age media items set as a favorite
#  1 : do not delete max age media items when set as a favorite
# (1 : default)
#----------------------------------------------------------#
max_keep_favorites_movie=1
max_keep_favorites_episode=1
max_keep_favorites_video=1
max_keep_favorites_trailer=1
max_keep_favorites_audio=1
```

#### Created first time the script runs; Do **_NOT_** edit or modify these:
```python
#------------DO NOT MODIFY BELOW---------------------------#

#----------------------------------------------------------#
# Server branding; chosen during setup
#  0 - 'emby'
#  1 - 'jellyfin'
#----------------------------------------------------------#
server_brand='abcd'

#----------------------------------------------------------#
# Server URL; created during setup
#----------------------------------------------------------#
server_url='http://localhost.abc:8096/basename'

#----------------------------------------------------------#
# Admin username; chosen during setup
#----------------------------------------------------------#
admin_username='Username'

#----------------------------------------------------------#
# Access token; requested from server during setup
#----------------------------------------------------------#
access_token='0123456789abcdef0123456789abcdef'

#----------------------------------------------------------#
# User key(s) of account(s) to monitor media items; chosen during setup
#----------------------------------------------------------#
user_keys='["abcdef0123456789abcdef0123456789", "fedcba9876543210fedcba9876543210", "9876543210fedcba9876543210fedcba", "etc..."]'

#----------------------------------------------------------#
# User blacklisted libraries of corresponding user account(s) to monitor media items; chosen during setup
#----------------------------------------------------------#
user_bl_libs='["/some/path/0,/some/path/1,/some/path/2", "/some/path/1,/some/path/2,/some/path/3", "/some/path/x,/some/path/etc..."]'

#----------------------------------------------------------#
# User whitelisted libraries of corresponding user account(s) to exclude monitoring media items; chosen during setup
#----------------------------------------------------------#
user_wl_libs='["/some/path/4,/some/path/5,/some/path/6", "/some/path/5,/some/path/6,/some/path/7", "/some/path/y,/some/path/etc..."]'

#----------------------------------------------------------#
# API request attempts; number of times to retry an API request
#  Delay between initial attempt and the first retry is 1 second
#  The delay will double with each try after the first retry
#  0-16 - number of retry attempts
#  (6 : default)
#----------------------------------------------------------#
api_request_attempts=6

#----------------------------------------------------------#
# API return limit; large libraries sometimes cannot return all of the media metadata items in a single API call
#  This is especially true when using the max_age_xyz options; the max_age_xyz options require every item of the specified media type send its metadata
#  1-10000 - number of media metadata items the server will return for each API call for media item metadata; ALL items will be processed regardless of this value
#  (100 : default)
#----------------------------------------------------------#
api_return_limit=100

#----------------------------------------------------------#
# 0 - Debug messages disabled
# 1 - Debug messages enabled
# (0 : default)
#----------------------------------------------------------#
DEBUG=0
```

# Usage
Make media_cleaner.py executable and run "python3.x /path/to/media_cleaner.py".  If no conifg file is found it will prompt you to create one.  Once done you can run the script again to view files that will be deleted

# Requirements
* python3
* python-dateutil
* Emby/Jellyfin need to have permissions to delete media items (read from [this post](https://github.com/clara-j/media_cleaner/issues/2#issuecomment-547319398) down)

# First Run
* $ /path/to/python3.x /path/to/media_cleaner.py
* You may get the below python error if the python-dateutil module is not installed
   - ModuleNotFoundError: No module named 'dateutil' python-dateutil
* For Debian/Ubuntu/Linux Mint type systems you can install the python-dateutil module with the following commands:
   - $ sudo apt-get update
   - $ sudo apt-get upgrade -y
   - $ sudo apt-get install python3-pip -y
   - $ sudo pip3 install -U pip
   - $ sudo pip3 install python-dateutil
* For other operating systems
   - Please consult Google

# Donation
If you find this useful and you would like to support please the use option below.

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/donate?hosted_button_id=4CFFHMJV3H4M2)
