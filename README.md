# Multi-User Media Cleaner
Multi-User Media Cleaner aka MUMC (pronounced Mew-Mick) will go through your movies, tv episodes, audio tracks, and audiobooks in your libraries and delete media items you no longer want taking up disk space.
# What Is Included?
## mumc.py
This is the main file. Without it you would still be looking for ways to automatically delete the media items you no longer want hanging around.
## mumc_config_defaults.py
_**Optional:**_ Before running the script for the first time; you can edit this file to customize the default values used when ```mumc_config.py``` is created. But do not worry if you forget to do this, you can always manually edit ```mumc_config.py``` later.
# Configuration
## mumc_config.py
Also referred to as ```mumc_config.py```. It is created the first time the script runs. Once it has been cretaed it will be what you edit to make MUMC delete the media items you want it to delete and keep the ones you want to keep.
# Cool! How Do I Use This?
## Step 1: Learn What A Filter Statement Is
### Objective - Get you comfortable with what a Filter Statement does.
* A Filter Statement is an simple way to tell this script how to find and delete the media items taking up your disk space.
  - This also means the media items not matching the Filter Statement are kept safe for watching at a later time.
## Step 2: How Do I Make A Filter Statement
### Objective - Help you understand the basics to building a generic Filter Statement.

* Generic Filter Statement Parts (each media type has their own Filter Statement Parts):
  - Part #1 - Condition
  - Part #2 - Condition Days
  - Part #3 - Play Count Inequality
  - Part #4 - Play Count

Start with a generic Filter Statement:
* Delete media type Part #1 at least Part #2 days ago with a play count Part #3 Part #4.

* Filling in the blanks for the generic Filter Statement above:
  - Part #1 - played
  - Part #2 - 60
  - Part #3 - >=
  - Part #4 - 1
    - Delete media type played at least 60 days ago with a play count >= 1.

* Filling in the blanks for the generic Filter Statement above using different values:
- Part #1 - created
  - Part #2 - 3650
  - Part #3 - <
  - Part #4 - 2
    - Delete media type created at least 3650 days ago with a play count < 2.
## Step 3: Build A Filter Statement For A Specific Media Type (i.e. movies, episodes, etc...)
### Objective - Show you how to build a Filter Statement for each media type.

* Delete movies played at least 22 days ago with a play count >= 1.
  - movie_condition='played'
  - movie_condition_days=22
  - movie_play_count_comparison='>='
  - movie_play_count=1

* Delete episodes played at least 55 days ago with a play count not <= 0.
  - episode_condition='played'
  - episode_condition_days=55
  - episode_play_count_comparison='not <='
  - episode_play_count=0

* Delete audio tracks played at least 123 days ago with a play count == 4.
  - audio_condition='played'
  - audio_condition_days=123
  - audio_play_count_comparison='=='
  - audio_play_count=4

* Delete episodes created at least 3456 days ago with a play count > 0.
  - episode_condition='created'
  - episode_condition_days=3456
  - episode_play_count_comparison='>'
  - episode_play_count=0

* Delete movies created at least 4567 days ago with a play count not == 0.
  - movie_condition='created'
  - movie_condition_days=4567
  - movie_play_count_comparison='not =='
  - movie_play_count=0

* Delete audio tracks created at least 5678 days ago with a play count not >= 11.
  - audio_condition='created'
  - audio_condition_days=5678
  - audio_play_count_comparison='not >='
  - audio_play_count=11

There are many many more possible combinations!

## Step 4: You Are Probably Thinking, "Well This Is Easy!". Well Yes It Is, BUT...
### Objective - Educate you on the dangers of ill-thought-out filters.
You are SOLEY RESPONSIBLE if you delete large portions of your library.
#### !!!DANGEROUS!!! Filter Examples Below !BEWARE!
What you NEVER want to do is to set ```*_condition='created'``` and ```*_condition_days=TO_SOME_LOW_NUMBER```.
Doing this WILL delete MOST if not ALL of your library.

##### Never do this unless you are 1000% confident it is doing exactly what you expect:
* Delete movies created at least 0 days ago...
  - movie_condition='created'
  - movie_condition_days=0
  - ...

* Delete episodes created at least 1 day ago...
  - episode_condition='created'
  - episode_condition_days=1
  - ...

* Delete audio track created at least 2 days ago...
  - audio_condition='created'
  - audio_condition_days=2
  - ...

* Delete movie created at least 3 days ago...
  - movie_condition='created'
  - movie_condition_days=3
  - ...

You get the point right?

## Step 5: Oh Yeah, Duh
### Objective - Here are some things to keep in mind when building Filter Statements

Filter Statements which imply played media items with only negative play counts, like the ones below, will evalute as play_count=0 (i.e. unplayed).

* ...with a play count < 0.
  - ...
  - episode_play_count_comparison='<'
  - episode_play_count=0

* ...with a play count not >= 0.
  - ...
  - movie_play_count_comparison='not >='
  - movie_play_count=0

Filter Statements with a played condition and a play count overlapping zero and non-zero numbers, like the ones shown below, will only delete the media items with non-zero play counts (i.e. the played media items).

* Delete episodes played at least 44 days ago with a play count <= 1.
  - episode_condition='played'
  - episode_condition_days=44
  - episode_play_count_comparison='<='
  - episode_play_count=1

* Delete movies played at least 88 days ago with a play count >= 0.
  - movie_condition='played'
  - movie_condition_days=88
  - movie_play_count_comparison='>='
  - movie_play_count=0

To make a Filter Statement that deletes played and unplayed media items CAREFULLY use the created condition, as shown below.

* Delete episodes created at least 2222 days ago with a play count <= 730500.
  - episode_condition='created'
  - episode_condition_days=2222
  - episode_play_count_comparison='<='
  - episode_play_count=730500

* Delete movies created at least 3333 days ago with a play count >= 0.
  - movie_condition='created'
  - movie_condition_days=3333
  - movie_play_count_comparison='>='
  - movie_play_count=0

To make a Filter Statement that deletes only unplayed media items CAREFULLY use the created condition, as shown below.

* Delete episodes created at least 7777 days ago with a play count == 0.
  - episode_condition='created'
  - episode_condition_days=7777
  - episode_play_count_comparison='=='
  - episode_play_count=0

* Delete movies created at least 9999 days ago with a play count not >= 1.
  - movie_condition='created'
  - movie_condition_days=9999
  - movie_play_count_comparison='not >='
  - movie_play_count=1
#  Contents Of The Configuration File
### Basic Configuration File Variables
#### Part #1 of the Filter Statement: _Condition_
```python
#----------------------------------------------------------#
# Condition: Delete media items based on when they were last played or
#             based on when they were created.
#   played - Filter will keep or delete media items based on last played date
#   created - Filter will keep or delete media items based on creation date
# (played : default)
#----------------------------------------------------------#
movie_condition='played'
episode_condition='played'
audio_condition='played'
audiobook_condition='played'
```
#### Part #2 of the Filter Statement: _Condition Days_
```python
#----------------------------------------------------------#
# Condition Days: Delete media items last played or created at least this many days ago
#   0-730500 - Number of days filter will use to determine when the media items was
#              last played or when the media item was created
#  -1 - To disable deleting specified media type
# (-1 : default)
#----------------------------------------------------------#
movie_condition_days=-1
episode_condition_days=-1
audio_condition_days=-1
audiobook_condition_days=-1
```
#### Part #3 of the Filter Statement: _Play Count Inequality_
```python
#----------------------------------------------------------#
# Play Count Inequality: Delete media items within this range based off of the chosen *_play_count.
#   > - Filter media items last played or created greater than *_play_count days ago
#   < - Filter media items last played or created less than *_play_count days ago
#   >= - Filter media items last played or created greater than or equal to *_play_count days ago
#   <= - Filter media items last played or created less than or equal to *_play_count days ago
#   == - Filter media items last played or created equal to *_play_count days ago
#   not > - Filter media items last played or created not greater than *_play_count days ago
#   not < - Filter media items last played or created not less than *_play_count days ago
#   not >= - Filter media items last played or created not greater than or equal to *_play_count days ago
#   not <= - Filter media items last played or created not less than or equal to *_play_count days ago
#   not == - Filter media items last played or created not equal to *_play_count days ago
# (>= : default)
#----------------------------------------------------------#
movie_play_count_comparison='>='
episode_play_count_comparison='>='
audio_play_count_comparison='>='
audiobook_play_count_comparison='>='
```
#### Part #4 of the Filter Statement: _Play Count_
```python
#----------------------------------------------------------#
# Play Count: Delete media items with a play count relative to this number.
#   0-730500 - Number of times a media item has been played
# (1 : default)
#----------------------------------------------------------#
movie_play_count=1
episode_play_count=1
audio_play_count=1
audiobook_play_count=1
```
### Advanced Configuration File Variables
#### Option for determining if a media item should be deleted or kept based on individual users' or all users' play counts:
```python
#----------------------------------------------------------#
# Decide how play count with multiple users will behave
#  0 - ok to delete media item when ANY monitored users meet the
#      *_play_count_comparison and *_play_count
#  1 - ok to delete media item when ALL monitored users meet the
#      *_play_count_comparison and *_play_count
# (0 : default)
#----------------------------------------------------------#
multiuser_play_count_movie=0
multiuser_play_count_episode=0
multiuser_play_count_audio=0
multiuser_play_count_audiobook=0
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
#### Option for determining if a media item should be deleted or kept based on other users' whitelisted libraries:
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
#### At least this many episodes will remain in each tv series:
```python
#----------------------------------------------------------#
# Decide the minimum number of episodes to remain in all tv series'
# Keeping one or more epsiodes for each series allows the "Next Up"m
#  functionality to notify user(s) when a new episode for a series
#  is ready to be watched
#  0 - Episodes will be deleted as they are watched
#  1-730500 - All but the latest "selected number" of episodes will be deleted as they are watched
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
#### Control output printed to the console
```python
#----------------------------------------------------------#
# Enable/Disable console outputs by type
#----------------------------------------------------------#
#  Should the script print its output to the console
#  False - Do not print this output type to the console
#  True - Print this output type to the console
# (True : default)
#----------------------------------------------------------#
print_script_header=True
print_warnings=True
print_user_header=True
print_movie_delete_info=True
print_movie_keep_info=True
print_movie_error_info=True
print_episode_delete_info=True
print_episode_keep_info=True
print_episode_error_info=True
print_audio_delete_info=True
print_audio_keep_info=True
print_audio_error_info=True
print_audiobook_delete_info=True
print_audiobook_keep_info=True
print_audiobook_error_info=True
print_summary_header=True
print_movie_summary=True
print_episode_summary=True
print_audio_summary=True
print_audiobook_summary=True
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
### Automatically Created Configuration File Variables
```python
#---------!!!DO NOT MODIFY ANYTHING BELOW!!!----------------#
# These are automatically created during setup.
#   If you do not know EXACTLY what you are doing, changing these
#      can and will cause script failure.
#   The only way to recover from script failure is to revert the
#      config back to the way it was OR rebuilding a new config.
#----------------------------------------------------------#
```
#### Needed for differences between Emby and Jellyfin
```python
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
#  (25 : default)
#----------------------------------------------------------#
api_query_item_limit=25
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
# Configuration file versions prior to 3.0.0 Are Not Compatible
* Previous ```mumc_config.py``` files made with script versions before 3.0.0 are NOT compatible.
  - A new ```mumc_config.py``` will need to be created using the latest version of this script.
# Requirements
* Linux or Windows
   - Mac - I do not have a Mac to confirm
   - If someone has confirmed this works on Mac, let me know and I will update this.
* Python 3.10
   - Older versions of python 3.x will likely work; but are not supported
   - Python 2.x or earlier are not supported and will not work
* python-dateutil \***must** be installed\*
* Emby/Jellyfin need to have OS level permissions on Linux machines to delete media items: [Read This Post](https://github.com/terrelsa13/MUMC/issues/28#issue-1293649223)

# Delete Or Keep Priorities Of A Media Item

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

# Blacklisting vs Whitelisting
* [Explaination and examples.](https://github.com/terrelsa13/MUMC/issues/27#issue-1293645665)

# Blacktagging vs Whitetagging
* [Explaination and examples.](https://github.com/terrelsa13/MUMC/issues/16#issue-1205993797)

# minimum_number_episodes=#
* [Explaination and examples.](https://github.com/terrelsa13/MUMC/issues/21#issue-1258905586)

# Library Matching By Id, By Path, or By Network Path
* [Explaination and examples.](https://github.com/terrelsa13/MUMC/issues/18#issue-1217953189)

# First Run (Debian, Ubuntu, and Linux Mint)
* Install Python version mentioned in the 'Requirements' section above
   - If this version of Python is not installed do NOT overwrite the OS default Python version
   - Instead use the link below to create an alternate install of Python
      - [Python 3.7.x example](https://tecadmin.net/install-python-3-7-on-ubuntu-linuxmint/)
* Install the python-dateutil module with the following commands:
   - $```sudo apt-get update```
   - $```sudo apt-get upgrade -y```
   - $```sudo apt-get install python3-pip -y```
   - $```pip3 install -U pip```
   - $```pip3 install python-dateutil```
* **\*OPTIONAL\*** Update the mumc_config_defaults.py file with desired default values
   - $```nano /path/to/mumc_config_defaults.py```
* Make the script executable
   - $```chmod +x /path/to/mumc.py```
* Run the script
   - $```/path/to/python3.x /path/to/mumc.py```
* First time the script is run, it will walk through building the mumc_config.py file

* If you get the below python error the python-dateutil module was not properly installed
   - ```ModuleNotFoundError: No module named 'dateutil' python-dateutil```

# First Run (Other Operating Systems)
* Please consult your favorite search engine

# Schedule To Run Using Crontab (Debian, Ubuntu, and Linux Mint)
* Below cron entry runs script everyday at 00:00hrs (aka 12AM)
   - $```0 0 * * * /usr/local/bin/python3.10 /opt/mumc/mumc.py```
* Below cron entry runs script every Monday at 01:23hrs (aka 1:23AM) and saves the output to a file called mumc.log in the /var/log/ directory
   - $```23 1 * * 1 /usr/local/bin/python3.10 /opt/mumc/mumc.py > /var/log/mumc.log 2>&1```

# Schedule To Run (Other Operating Systems)
* Please consult your favorite search engine

# Donation
If you find this script useful and would like to show support, please consider the option below.

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/donate?hosted_button_id=4CFFHMJV3H4M2)
