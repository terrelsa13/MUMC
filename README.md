# Multi-User Media Cleaner
Multi-User Media Cleaner aka MUMC (pronounced Mew-Mick) will go through movies, tv episodes, audio tracks, and audiobooks in your Emby/Jellyfin libraries and delete media items you no longer want taking up disk space.
# What Files Are Included?
## mumc.py
This is the main file. Without it you would still be looking for ways to automatically delete the media items you no longer want hanging around.
## mumc_config_defaults.py
_**Optional:**_ Before running the script for the first time; you can edit this file to customize the default values used when ```mumc_config.py``` is created. But do not worry if you forget to do this, you can always manually edit ```mumc_config.py``` after it is created.
# Configuration
## mumc_config.py
```mumc_config.py```, also referred to as the _configuration file_, is created the first time the script runs. Once it has been cretaed it will be what you edit to configure MUMC to delete the media items you want it to delete and keep the media items you want to keep.
# Cool! How Do I Use This?
## Step 1: What is a Filter Statement? What is a Behavioral Statement?

* A Filter Statement is a simple way to tell the script how to find media items taking up your disk space.
* A Behavioral Statement is a simple way to tell the script how to delete media items found with the Filter Statement.
  - This also means the media items **not matching** the Filter Statement and Behavioral Statement are kept safe for watching later.
## Step 2: The basics of building a generic Filter Statement.

Generic Filter Statement Parts (each media type has their own Filter Statement Parts):
* **Part #1** - Condition Days
* **Part #2** - Played Count Inequality
* **Part #3** - Played Count

Starting with generic Filter Statements:
* Find media items Played/Created at least **Part #1** days ago with a played count **Part #2** **Part #3**.

  - Example A: Filling in the blanks for a generic media items _played_ Filter Statement:
    - Part #1** - **60**
    - Part #2** - **>=**
    - Part #3** - **1**
      - Find media items _played_ at least **60** days ago with a played count **>=** **1**.

  - Example B: Filling in the blanks for a generic media items _created_ Filter Statement:
    - Part #1 - **3650**
    - Part #2 - **<**
    - Part #3 - **2**
      - Find media items _created_ at least **3650** days ago with a played count **<** **2**.
## Step 3: Building Filter Statements for specific media types.

* Find movies played at least **22** days ago with a played count **>=** **1**.
  - played_filter_movie=[22,'>=',1]

* Find episodes played at least **55** days ago with a played count **not <=** **0**.
- played_filter_episode=[55,'not <=',0]

* Find audio tracks played at least **123** days ago with a played count **==** **4**.
  - played_filter_audio=[123,'==',4]

* Find episodes created at least **3456** days ago with a played count **>** **0**.
  - episode_created_days=3456
  - episode_created_played_count_comparison='>'
  - episode_created_played_count=0

* Find movies created at least **4567** days ago with a played count **not ==** **0**.
  - movie_created_days=4567
  - movie_created_played_count_comparison='not =='
  - movie_created_played_count=0

* Find audio tracks created at least **5678** days ago with a played count **not >=** **11**.
  - audio_created_days=5678
  - audio_created_played_count_comparison='not >='
  - audio_created_played_count=11

There are many possible combinations!

## Step 4: The dangers of ill-thought-out Filter Statements.

You are **SOLEY RESPONSIBLE** if you misconfigure your Filter Statement and delete large portions of your library. I recommend staying in dry-run mode until you are certain things are working exactly as you want them to.
#### !!!DANGEROUS Filter Examples Below BEWARE!!!
What you **_NEVER_** want to do is to set ```*_created_days=TO_SOME_LOW_NUMBER```.
Doing this WILL delete MOST if not ALL of your library.
##### Never do this unless you are 1000% confident it is doing exactly what you expect:
* Find movies created at least **0** days ago...
  - movie_created_days=0
  - ...

* Find episodes created at least **1** day ago...
  - episode_created_days=1
  - ...

* Find audio track created at least **2** days ago...
  - audio_created_days=2
  - ...

* Find movie created at least **3** days ago...
  - movie_created_days=3
  - ...

You get the point right?

## Step 5: A couple things to remember when building Filter Statements.

Filter Statements implying negative played counts will be evaluted as ```*_played_count=0``` (i.e. unplayed media items).

* ...with a played count **<** **0**.
  - ...
  - episode_played_count_comparison='<'
  - episode_played_count=0

* ...with a played count **not >=** **0**.
  - ...
  - movie_created_played_count_comparison='not >='
  - movie_created_played_count=0

_Played_ Filter Statements overlapping zero and postive numbered played counts will only delete the media items with postive numbered played counts (i.e. the played media items).

* Find episodes played at least # days ago with a played count **<=** **1**.
  - ...
  - episode_played_count_comparison='<='
  - episode_played_count=1

* Find movies played at least # days ago with a played count **>=** **0**.
  - ...
  - movie_played_count_comparison='>='
  - movie_played_count=0

## Step 6: Example Filter Statements.

#### Filter Statement to delete movies played 90 or more days ago.

* Find movies played at least **90** days ago with a played count **>=** **1**.
  - movie_played_days=90
  - movie_played_count_comparison='>='
  - movie_played_count=1

#### Filter Statement to delete episodes played less than twice, 30 or more days ago.

* Find episodes played at least **30** days ago with a played count **<** **2**.
  - episode_played_days=30
  - episode_played_count_comparison='<'
  - episode_played_count=2

#### Filter Statement to delete "old" played and unplayed movies.

* Find movies created at least **365** days ago with a played count **>=** **0**.
  - movie_created_days=365
  - movie_created_played_count_comparison='>='
  - movie_created_played_count=0

#### Filter Statement to delete "old" unplayed episodes.

* Find episodes created at least **365** days ago with a played count **==** **0**.
  - episode_created_days=365
  - episode_created_played_count_comparison='=='
  - episode_created_played_count=0

#### Filter Statement to delete "old" played episodes.

* Find episodes created at least **365** days ago with a played count **not ==** **0**.
  - episode_created_days=365
  - episode_created_played_count_comparison='not =='
  - episode_created_played_count=0

### Using Both Played And Created Filter Statements Together:
#### Filter Statement to delete movies played exactly once, 60 or more days ago.
#### Combined with...
#### Filter Statement to delete unplayed movies created 180 or more days ago.

* Find movies played at least **60** days ago with a played count **==** **1**.
  - movie_played_days=60
  - movie_played_count_comparison='=='
  - movie_played_count=1

* Find movies created at least **180** days ago with a played count **==** **0**.
  - movie_created_days=180
  - movie_created_played_count_comparison='=='
  - movie_created_played_count=0

## Step 7: The basics of building a generic Behavioral Statement.

__Behavioral Statements apply to:__
* Favorites
* Whitetags
* Blacktags
* Whitelists
* Blacklists

#### [X, Y, Z, #]

Generic Behavioral Statement Parts (each media type has their own Behavioral Statement Parts):
* **Part #1** - Action (X : Keep or Delete)
* **Part #2** - User Conditional (Y : All or Any)
* **Part #3** - Played Conditional (Z : All, Any, or Ignore)
* **Part #4** - Action Control (# : 0 thru 8)

* The Behavior Statement is processed as follows:
  *  **Step #1** - Determine (Y) if the media item is Favorited/Whitetagged/Blacktagged/Whitelisted/Blacklisted for ALL monitored users or ANY monitored users; ```True``` or ```False``` is the result
  *  **Step #2** - Determine (Z) if the media item meets played days and played count for ALL monitored users or ANY monitored users; ```True``` or ```False``` is the result
  *  **Step #3** -  ```(Y and Z)``` **Step #1** and **Step #2**; ```True``` or ```False``` is the result
  *  **Step #4** - Look up the desired Action Control (#)
  *  **Step #5** - If the Action Control from **Step #4** allows; Take the result from **Step #3** and perform the Action (X); i.e. keep media item or delete media item

Starting with generic Behavioral Statements:

* **Part #1** favorited media item when **Part #2** monitored user(s) have it favorited and after **Part #3** monitored user(s) meet *_played_days and *_played_count

  - Example A: Filling in the blanks for a generic Favorites Behavioral Statement:
    - Part #1 - **Delete**
    - Part #2 - **Any**
    - Part #3 - **All**
      - **Delete** favorited media item when **Any** monitored user(s) have it favorited and after **All** monitored user(s) meet *_played_days and *_played_count.

* **Part #1** blacktagged media item when **Part #2** monitored user(s) have it blacktagged and after **Part #3** monitored user(s) meet *_played_days and *_played_count

  - Example B: Filling in the blanks for a generic Blacktags Behavioral Statement:
    - Part #1 - **Delete**
    - Part #2 - **All**
    - Part #3 - **Any**
      - **Delete** blacktagged media item when **All** monitored user(s) have it blacktagged and after **Any** monitored user(s) meet *_played_days and *_played_count.

* **Part #1** whitelisted media item when **Part #2** monitored user(s) have it favorited

  - Example C: Filling in the blanks for a generic Whitelistes Behavioral Statement:
    - Part #1 - **Keep**
    - Part #2 - **Any**
    - Part #3 - **Ignore**
      - **Keep** whitelisted media item when **Any** monitored user(s) have it whitelisted.

* **Part #1** favorited media item

  - Example D: Filling in the blanks for a generic Favorites Behavioral Statement:
    - Part #1 - **Keep**
    - Part #2 - **Any**
    - Part #3 - **Ignore**
      - **Keep** favorited media item.

## Step 8: Use (#) to decide when keep/delete Action (X) is performed.

#### **Part #4** Decide when the configured Action (X) from Step 7 is taken:
* No Action (X) taken on ```True``` - Delete or Keep is not performed when ```(Y and Z)``` is ```True```
* No Action (X) taken on ```False``` - Delete or Keep is not performed when ```(Y and Z)``` is ```False```
* Action (X) taken on ```True``` - Delete or Keep is performed when ```(Y and Z)``` is ```True```
* Action (X) taken on ```False``` - Delete or Keep is performed when ```(Y and Z)``` is ```False```
* Opposite Action (X) taken on ```True``` - Inverse of Delete or Keep is performed when ```(Y and Z)``` is ```True```
* Opposite Action (X) taken on ```False``` - Inverse of Delete or Keep is performed when ```(Y and Z)``` is ```False```

#### Possible Action Control **Part #4** combinations:
* 0 - No Action (X) taken on ```True```; No Action (X) taken on ```False``` (disabled)
* 1 - No Action (X) taken on ```True```; Action (X) taken on ```False```
* 2 - No Action (X) taken on ```True```; Opposite Action (X) taken on ```False```
* 3 - Action (X) taken on ```True```; No Action (X) taken on ```False``` (recommended)
* 4 - Action (X) taken on ```True```; Action (X) taken on ```False```
* 5 - Action (X) taken on ```True```; Opposite Action (X) taken on ```False``` (recommended)
* 6 - Opposite Action (X) taken on ```True```; No Action (X) taken on ```False```
* 7 - Opposite Action (X) taken on ```True```; Action (X) taken on ```False```
* 8 - Opposite Action (X) taken on ```True```; Opposite Action (X) taken on ```False```
#### Information
* **0**, **3**, or **5** are the recommended Action Controls (#).
  * 1,2,4,6,7,8 are special use case Action Controls; these are NOT recommended and NOT supported.
    * Use at your own discretion.

## Step 9: Building Behavioral Statements for specific media types.

* **Keep** favorited episode when **any** monitored users have it favorited.
  * favorited_behavior_episode=['keep', 'any', 'ignore', 3]

* **Delete** blacklisted audio when **all** monitored users have it blacklisted.
  * blacklisted_behavior_audio=['delete', 'all', 'ignore', 3]

* **Delete** favorited episode when **any** monitored users have it blacklisted and **all** monitored users meet episode_played_days and episode_played_count.
  * blacklisted_behavior_audio=['delete', 'all', 'ignore', 5]

* **Delete** whitelisted movie when **any** monitored users have it whitelisted and **all** monitored users meet movie_played_days and movie_played_count.
  * whitelisted_behavior_movie=['delete', 'any', 'all', 3]

* **Delete** whitetagged episode when **all** monitored users have it whitetagged and **any** monitored users meet episode_played_days and episode_played_count.
  * whitelisted_behavior_episode=['delete', 'all', 'any', 3]

* **DISABLE** favoited movies. [X (keep or delete), Y (all or any), Z (all or any), Action Control (#) 0]
  * favorited_behavior_episode=['X', 'Y', 'Z', 0]

#### Tip:
* **Keep** - Removes the media item from the delete list
* **Delete** - Adds the media item to the delete list

#  Contents Of The Configuration File
### Basic Configuration File Variables
#### Played Filter Statements:
```python
#----------------------------------------------------------#
# Played Filter Statements
#
# [A,B,C]
#
# A - Condition Days
# B - Played Count Inequality
# C - Played Count
#
# Condition Days (A): Find media items last played this many days ago
#   0-730500 - Number of days filter will use to determine when the media item was last played
#  -1 - To disable deleting specified media type
#
# Played Count Inequality (B): Delete media items within this range based off of the chosen *_played_count.
#   > - Filter media items with a played count greater than *_played_count days ago
#   < - Filter media items with a played count less than *_played_count days ago
#   >= - Filter media items with a played count greater than or equal to *_played_count days ago
#   <= - Filter media items with a played count less than or equal to *_played_count days ago
#   == - Filter media items with a played count equal to *_played_count days ago
#   not > - Filter media items with a played count not greater than *_played_count days ago
#   not < - Filter media items with a played count not less than *_played_count days ago
#   not >= - Filter media items with a played count not greater than or equal to *_played_count days ago
#   not <= - Filter media items with a played count not less than or equal to *_played_count days ago
#   not == - Filter media items with a played count not equal to *_played_count days ago
#
# Played Count (C): Find media items with a played count relative to this number.
#   1-730500 - Number of times a media item has been played
#
# ([-1,'>=',1] : default)
#----------------------------------------------------------#
played_filter_movie=[-1, '>=', 1]
played_filter_episode=[-1, '>=', 1]
played_filter_audio=[-1, '>=', 1]
played_filter_audiobook=[-1, '>=', 1]
```
#### Created Filter Statements:
```python
#----------------------------------------------------------#
# Created Filter Statements
#
# [A,B,C,D]
#
# A - Condition Days
# B - Played Count Inequality
# C - Played Count
# D - Behaviorial Control
#
# Condition Days (A): Find media items created at least this many days ago
#   0-730500 - Number of days filter will use to determine when the media item was created
#  -1 - To disable deleting specified media type
#
# Played Count Inequality (B): Delete media items within this range based off of the chosen *_played_count.
#   > - Filter media items with a played count greater than *_played_count days ago
#   < - Filter media items with a played count less than *_played_count days ago
#   >= - Filter media items with a played count greater than or equal to *_played_count days ago
#   <= - Filter media items with a played count less than or equal to *_played_count days ago
#   == - Filter media items with a played count equal to *_played_count days ago
#   not > - Filter media items with a played count not greater than *_played_count days ago
#   not < - Filter media items with a played count not less than *_played_count days ago
#   not >= - Filter media items with a played count not greater than or equal to *_played_count days ago
#   not <= - Filter media items with a played count not less than or equal to *_played_count days ago
#   not == - Filter media items with a played count not equal to *_played_count days ago
#
# Played Count (C): Find media items with a played count relative to this number.
#   0-730500 - Number of times a media item has been played
#
# Behavioral Control (D): Determine if favorited_behavior_*, whitetagged_behavior_*, blacktagged_behavior_*,
#  whitelisted_behavior_*, and blacklisted_behavior_* apply to media items meeting the created_filter_*.
#   False - Media items meeting the created_filter_* will be deleted regardless of favorited_behavior_*,
#    whitetagged_behavior_*, blacktagged_behavior_*, whitelisted_behavior_*, and blacklisted_behavior_*
#   True - Media items meeting the created_filter_* will also have to meet configured behaviors; favorited_behavior_*,
#    whitetagged_behavior_*, blacktagged_behavior_*, whitelisted_behavior_*, and blacklisted_behavior_*
#
# ([-1,'>=',1,True] : default)
#----------------------------------------------------------#
created_filter_movie=[-1, '>=', 1, True]
created_filter_episode=[-1, '>=', 1, True]
created_filter_audio=[-1, '>=', 1, True]
created_filter_audiobook=[-1, '>=', 1, True]
```
### Advanced Configuration File Variables
#### Favorited Behavioral Statements:
```python
#----------------------------------------------------------#
# Favorited Behavioral Statements
#
# Favoriting is the first (and highest) priority
#  Whitetagging behavior is ignored
#  Blacktagging behavior is ignored
#  Whitelisting behavior is ignored
#  Blacklisting behavior is ignored
#
# [W, X, Y, Z]
#
# W - Action
# X - User Conditional
# Y - Played Conditional
# Z - Action Control
#
# Action (W): Specify which action should be taken when (X) and (Y) is True.
#   delete - Delete media item from server
#   keep - Do NOT delete media item from server
#
# User Conditional (X): Specify how monitored users must have the media item favorited.
#   all - Every monitored user must have the media item favorited
#   any - One or more monitored users must have the media item favorited
#
# Played Conditional (Y): Specify how monitored users must meet played_filter_*.
#   all - Every monitored user must meet the played_filter_*
#   any - One or more monitored users must meet the played_filter_*
#   ignore - Ignore if monitored users meet the played_filter_*
#
# Action Control (Z): Specify the action the script will take when (X) and (Y) is True/False
#   0 - No action taken on True; No action taken on False (disabled)
#   1 - No action taken on True; Action taken on False
#   2 - No action taken on True; Opposite action taken on False
#   3 - Action taken on True; No action taken on False (recommended)
#   4 - Action taken on True; Action taken on False
#   5 - Action taken on True; Opposite action taken on False (recommended)
#   6 - Opposite action taken on True; No action taken on False
#   7 - Opposite action taken on True; Action taken on False
#   8 - Opposite action taken on True; Opposite action taken on False
#
# (['keep','any','ignore',3] : default)
#----------------------------------------------------------#
favorited_behavior_movie=['keep', 'any', 'ignore', 3]
favorited_behavior_episode=['keep', 'any', 'ignore', 3]
favorited_behavior_audio=['keep', 'any', 'ignore', 3]
favorited_behavior_audiobook=['keep', 'any', 'ignore', 3]
```
#### Keep movie if genre favorited:
```python
#----------------------------------------------------------#
# Advanced movie favorites configurations
#     Requires 'favorites_behavior_movie>=1'
#----------------------------------------------------------#
#  Keep movie based on the genres
#  0 - ok to delete movie when genres are set as a favorite
#  1 - keep movie if FIRST genre listed is set as a favorite
#  2 - keep movie if ANY genre listed is set as a favorite
# (0 : default)
#----------------------------------------------------------#
favorites_advanced_movie_genre=0
favorites_advanced_movie_library_genre=0
```
#### Keep episode if genre or studio-network favorited:
```python
#----------------------------------------------------------#
# Advanced episode favorites configurations
#     Requires 'favorites_behavior_episode>=1'
#----------------------------------------------------------#
#  Keep episode based on the genre(s) or studio-network(s)
#  0 - ok to delete episode when its genres or studio-networks are set as a favorite
#  1 - keep episode if FIRST genre or studio-network is set as a favorite
#  2 - keep episode if ANY genres or studio-networks are set as a favorite
# (0 : default)
#----------------------------------------------------------#
favorites_advanced_episode_genre=0
favorites_advanced_season_genre=0
favorites_advanced_series_genre=0
favorites_advanced_tv_library_genre=0
favorites_advanced_tv_studio_network=0
favorites_advanced_tv_studio_network_genre=0
```
#### Keep track if genre or artist favorited:
```python
#----------------------------------------------------------#
# Advanced track favorites configurations
#     Requires 'favorites_behavior_audio>=1'
#----------------------------------------------------------#
#  Keep track based on the genre(s) or artist(s)
#  0 - ok to delete track when its genres or artists are set as a favorite
#  1 - keep track if FIRST genre or artist is set as a favorite
#  2 - keep track if ANY genres or artists are set as a favorite
# (0 : default)
#----------------------------------------------------------#
favorites_advanced_track_genre=0
favorites_advanced_album_genre=0
favorites_advanced_music_library_genre=0
favorites_advanced_track_artist=0
favorites_advanced_album_artist=0
```
#### Keep audio book track if genre or author favorited:
```python
#----------------------------------------------------------#
# Advanced audio book favorites configurations
#     Requires 'favorites_behavior_audiobook>=1'
#----------------------------------------------------------#
#  Keep audio book track based on the genres or authors
#  0 - ok to delete audio book track when its genres or authors are set as a favorite
#  1 - keep audio book track if FIRST genre or author is set as a favorite
#  2 - keep audio book track if ANY genres or authors are set as a favorite
# (0 : default)
#----------------------------------------------------------#
favorites_advanced_audiobook_track_genre=0
favorites_advanced_audiobook_genre=0
favorites_advanced_audiobook_library_genre=0
favorites_advanced_audiobook_track_author=0
favorites_advanced_audiobook_author=0
```
#### Whitetag a media item to be kept after it is played:
```python
#----------------------------------------------------------#
# User entered whitetag name; chosen during setup
#  Use a comma ',' to seperate multiple tag names
#   Ex: tagname,tag name,tag-name
#  Backslash '\' not allowed
#----------------------------------------------------------#
whitetag='white_tagname,white_tag name,white_tag-name'
```
#### Whitetagged Behavioral Statements:
```python
#----------------------------------------------------------#
# Whitetagged Behavioral Statements
#  Tags applied to a media item are seen by all users
#
# Whitetagging is the second priority
#  Blacktagging behavior is ignored
#  Whitelisting behavior is ignored
#  Blacklisting behavior is ignored
#
# [W, X, Y, Z]
#
# W - Action
# X - User Conditional
# Y - Played Conditional
# Z - Action Control
#
# Action (W): Specify which action should be taken when (X) and (Y) is True.
#   delete - Delete media item from server
#   keep - Do NOT delete media item from server
#
# User Conditional (X): Specify how monitored users must have the media item whitetagged.
#   all - Every monitored user must have the media item whitetagged
#   any - N/A; Tags apply to all users
#
# Played Conditional (Y): Specify how monitored users must meet played_filter_*.
#   all - Every monitored user must meet the played_filter_*
#   any - One or more monitored users must meet the played_filter_*
#   ignore - Ignore if monitored users meet the played_filter_*
#
# Action Control (Z): Specify the action the script will take when (X) and (Y) is True/False
#   0 - No action taken on True; No action taken on False (disabled)
#   1 - No action taken on True; Action taken on False
#   2 - No action taken on True; Opposite action taken on False
#   3 - Action taken on True; No action taken on False (recommended)
#   4 - Action taken on True; Action taken on False
#   5 - Action taken on True; Opposite action taken on False (recommended)
#   6 - Opposite action taken on True; No action taken on False
#   7 - Opposite action taken on True; Action taken on False
#   8 - Opposite action taken on True; Opposite action taken on False
#
# (['keep','all','ignore',0] : default)
#----------------------------------------------------------#
whitetagged_behavior_movie=['keep', 'all', 'ignore', 0]
whitetagged_behavior_episode=['keep', 'all', 'ignore', 0]
whitetagged_behavior_audio=['keep', 'all', 'ignore', 0]
whitetagged_behavior_audiobook=['keep', 'all', 'ignore', 0]
```
#### Blacktag a media item to be deleted after it is played:
```python
#----------------------------------------------------------#
# User entered blacktag name; chosen during setup
#  Use a comma ',' to seperate multiple tag names
#   Ex: tagname,tag name,tag-name
#  Backslash '\' not allowed
#----------------------------------------------------------#
blacktag='black_tagname,black_tag name,black_tag-name'
```
#### Blacktagged Behavioral Statements:
```python
#----------------------------------------------------------#
# Blacktagged Behavioral Statements
#  Tags applied to a media item are seen by all users
#
# Blacktagging is the third priority
#  Whitelisting behavior is ignored
#  Blacklisting behavior is ignored
#
# [W, X, Y, Z]
#
# W - Action
# X - User Conditional
# Y - Played Conditional
# Z - Action Control
#
# Action (W): Specify which action should be taken when (X) and (Y) is True.
#   delete - Delete media item from server
#   keep - Do NOT delete media item from server
#
# User Conditional (X): Specify how monitored users must have the media item blacktagged.
#   all - Every monitored user must have the media item blacktagged
#   any - N/A; Tags apply to all users
#
# Played Conditional (Y): Specify how monitored users must meet played_filter_*.
#   all - Every monitored user must meet the played_filter_*
#   any - One or more monitored users must meet the played_filter_*
#   ignore - Ignore if monitored users meet the played_filter_*
#
# Action Control (Z): Specify the action the script will take when (X) and (Y) is True/False
#   0 - No action taken on True; No action taken on False (disabled)
#   1 - No action taken on True; Action taken on False
#   2 - No action taken on True; Opposite action taken on False
#   3 - Action taken on True; No action taken on False (recommended)
#   4 - Action taken on True; Action taken on False
#   5 - Action taken on True; Opposite action taken on False (recommended)
#   6 - Opposite action taken on True; No action taken on False
#   7 - Opposite action taken on True; Action taken on False
#   8 - Opposite action taken on True; Opposite action taken on False
#
# (['delete','all','any',0] : default)
#----------------------------------------------------------#
blacktagged_behavior_movie=['delete', 'all', 'any', 0]
blacktagged_behavior_episode=['delete', 'all', 'any', 0]
blacktagged_behavior_audio=['delete', 'all', 'any', 0]
blacktagged_behavior_audiobook=['delete', 'all', 'any', 0]
```
#### Whitelisted Behavioral Statements:
```python
#----------------------------------------------------------#
# Whitelisted Behavioral Statements
#
# Whitelisting is the fourth priority
#  Blacklisting behavior is ignored
#
# [W, X, Y, Z]
#
# W - Action
# X - User Conditional
# Y - Played Conditional
# Z - Action Control
#
# Action (W): Specify which action should be taken when (X) and (Y) is True.
#   delete - Delete media item from server
#   keep - Do NOT delete media item from server
#
# User Conditional (X): Specify how monitored users must have the media item whitelisted.
#   all - Every monitored user must have the media item whitelisted
#   any - One or more monitored users must have the media item whitelisted
#
# Played Conditional (Y): Specify how monitored users must meet played_filter_*.
#   all - Every monitored user must meet the played_filter_*
#   any - One or more monitored users must meet the played_filter_*
#   ignore - Ignore if monitored users meet the played_filter_*
#
# Action Control (Z): Specify the action the script will take when (X) and (Y) is True/False
#   0 - No action taken on True; No action taken on False (disabled)
#   1 - No action taken on True; Action taken on False
#   2 - No action taken on True; Opposite action taken on False
#   3 - Action taken on True; No action taken on False (recommended)
#   4 - Action taken on True; Action taken on False
#   5 - Action taken on True; Opposite action taken on False (recommended)
#   6 - Opposite action taken on True; No action taken on False
#   7 - Opposite action taken on True; Action taken on False
#   8 - Opposite action taken on True; Opposite action taken on False
#
# (['keep','any','ignore',3] : default)
#----------------------------------------------------------#
whitelisted_behavior_movie=['keep', 'any', 'ignore', 3]
whitelisted_behavior_episode=['keep', 'any', 'ignore', 3]
whitelisted_behavior_audio=['keep', 'any', 'ignore', 3]
whitelisted_behavior_audiobook=['keep', 'any', 'ignore', 3]
```
#### Blacklisted Behavioral Statements:
```python
#----------------------------------------------------------#
# Blacklisted Behavioral Statements
#
# Blacklisting is the fifth (and lowest) priority
#
# [W, X, Y, Z]
#
# W - Action
# X - User Conditional
# Y - Played Conditional
# Z - Action Control
#
# Action (W): Specify which action should be taken when (X) and (Y) is True.
#   delete - Delete media item from server
#   keep - Do NOT delete media item from server
#
# User Conditional (X): Specify how monitored users must have the media item blacklisted.
#   all - Every monitored user must have the media item blacklisted
#   any - One or more monitored users must have the media item blacklisted
#
# Played Conditional (Y): Specify how monitored users must meet played_filter_*.
#   all - Every monitored user must meet the played_filter_*
#   any - One or more monitored users must meet the played_filter_*
#   ignore - Ignore if monitored users meet the played_filter_*
#
# Action Control (Z): Specify the action the script will take when (X) and (Y) is True/False
#   0 - No action taken on True; No action taken on False (disabled)
#   1 - No action taken on True; Action taken on False
#   2 - No action taken on True; Opposite action taken on False
#   3 - Action taken on True; No action taken on False (recommended)
#   4 - Action taken on True; Action taken on False
#   5 - Action taken on True; Opposite action taken on False (recommended)
#   6 - Opposite action taken on True; No action taken on False
#   7 - Opposite action taken on True; Action taken on False
#   8 - Opposite action taken on True; Opposite action taken on False
#
# (['delete','any','any',3] : default)
#----------------------------------------------------------#
blacklisted_behavior_movie=['delete', 'any', 'any', 3]
blacklisted_behavior_episode=['delete', 'any', 'any', 3]
blacklisted_behavior_audio=['delete', 'any', 'any', 3]
blacklisted_behavior_audiobook=['delete', 'any', 'any', 3]
```
#### At least this many episodes will remain in each tv series; Does not care about played or unplayed states:
```python
#----------------------------------------------------------#
# Decide the minimum number of episodes to remain in all tv series'
# This ignores the played and unplayed states of episodes
#  0 - Episodes will be deleted based on the Filter and Behavioral Statements
#  1-730500 - Episodes will be deleted based on the Filter and Behavioral Statements;
#              unless the remaining played and unplayed episodes are less than or
#              equal to the chosen value
# (0 : default)
#----------------------------------------------------------#
minimum_number_episodes=0
```
#### At least this many played episodes will remain in each tv series:
```python
#----------------------------------------------------------#
# Decide the minimum number of played episodes to remain in all tv series'
# Keeping one or more played epsiodes for each series allows the "Next Up"
#  functionality to notify user(s) when a new episode for a series
#  is available
# This value applies only to played and episodes
#  0 - Episodes will be deleted based on the Filter and Behavioral Statements
#  1-730500 - Episodes will be deleted based on the Filter and Behavioral Statements;
#              unless the remaining played episodes are less than or equal to the
#              chosen value
# (0 : default)
#----------------------------------------------------------#
minimum_number_played_episodes=0
```
#### Set the behavior of ```minimum_number_episodes``` and/or ```minimum_number_played_episodes```:
```python
#----------------------------------------------------------#
# Decide how 'minimum_number_episodes' and 'minimum_number_played_episodes' will behave.
# The minimum number of played and unplayed episodes will vary for each user and for each
#  series when multiple users are watching the same series at different paces.
# The following option gives a mechanism to control this in different ways.
# The 'minimum_number_episodes' and 'minimum_number_played_episodes' will be based off of...
#  'User's Name' - The UserName specified; If matching UserName not found script will assume default.
#  'User's Id' - The UserId specified; If matching UserName not found script will assume default.
#  'Max Played' - The first user with the highest number of played episodes to be deleted for each series.
#  'Min Played' - The first user with the lowest number of played episodes to be deleted for each series.
#  'Max Unplayed' - The first user with the highest number of unplayed episodes to be deleted for each series.
#  'Min Unplayed' - The first user with the lowest number of unplayed episodes to be deleted for each series.
# The Max/Min Played/Unplayed values can be mixed and matched. For example...
#  'Max Unplayed Min Played' - The number played episodes to be deleted is based off the user
#                                with the highest number of unplayed episodes to be deleted for a
#                                specified series. The number of unplayed episodes to be deleted is
#                                based off the user with the lowest number of played episodes to be
#                                deleted for a specified series.
# ('Min Played Min Unplayed' : default)
#----------------------------------------------------------#
minimum_number_episodes_behavior='Min Played Min Unplayed'
```
#### Add LastPlayedDate for media items without it
```python
#----------------------------------------------------------#
# Add last played date for items missing the LastPlayedDate data
# When played state is imported from Trakt the LastPlayedDate is
#  not populated. To allow the script to maintain functionality
#  the current date and time the script is run can be used as the
#  LastPlayedDate value.
#  False - Do not set the LastPlayedDate; days since played will show as
#        the number of days since 1970-Jan-01 00:00:00hrs for any media
#        items missng the LastPlayedDate data.
#  True - Set the LastPlayedDate; the current date-time the script is
#        run will be saved as the LastPlayedDate for any media items
#        missing the LastPlayedDate data. Only media items missing the
#        LastPlayedDate data are modified
# (True : default)
#----------------------------------------------------------#
movie_set_missing_last_played_date=True
episode_set_missing_last_played_date=True
audio_set_missing_last_played_date=True
audiobook_set_missing_last_played_date=True
```
#### Control output printed to the console
```python
#----------------------------------------------------------#
# Enable/Disable console outputs by type
#----------------------------------------------------------#
# Should the script print its output to the console
#  False - Do not print this output type to the console
#  True - Print this output type to the console
# (True : default)
#----------------------------------------------------------#
print_script_header=True
print_warnings=True
print_user_header=True
print_movie_delete_info=True
print_movie_keep_info=True
print_episode_delete_info=True
print_episode_keep_info=True
print_audio_delete_info=True
print_audio_keep_info=True
print_audiobook_delete_info=True
print_audiobook_keep_info=True
print_summary_header=True
print_movie_summary=True
print_episode_summary=True
print_audio_summary=True
print_audiobook_summary=True
print_script_footer=True
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
server_brand='server brand'
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
#  0 - blacklist - Chosen libraries will blacklisted
#                  All other libraries will be whitelisted
#  1 - whitelist - Chosen libraries will whitelisted
#                  All other libraries will be blacklisted
# (blacklist : default)
#----------------------------------------------------------#
library_setup_behavior='abclist'
```
#### How will media items be matched to their respective libraries?
```python
#----------------------------------------------------------#
# Decide how the script will match media items to libraries
#  0 - byId - Media items will be matched to libraries using 'LibraryIds'
#  1 - byPath - Media items will be matched to libraries using 'Paths'
#  2 - byNetwork Path - Media items will be matched to libraries using 'NetworkPaths'
# Filtering byId does not apply to the rules below.
# Filtering byPath requires no shared network folders are configured.
# Filtering byNetworkPath requires shared network folders are configured.
# (byId : default)
#----------------------------------------------------------#
library_matching_behavior='byAbc'
```
#### UserId for each monitored user
```python
#----------------------------------------------------------#
# User UserName(s) and UserId(s) of monitored account(s); chosen during setup
# The order of the UserName(s):UserId(s) here must match the order of the
#  UserId(s)/UserNames(s) in user_bl_libs and user_wl_libs
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
user_bl_libs='[{"userid": "abcdef0123456789abcdef0123456789", "username": "user1", "#": {"libid": "00112233445566778899aabbccddeeff", "collectiontype": "abc", "networkpath": "smb://some/netpath/0", "path": "/some/path/0"}, "#": {"libid": "aabbccddeeff00112233445566778899", "collectiontype": "def", "networkpath": "smb://some/netpath/1", "path": "/some/path/1"}}, {"etc...": "etc...", "#": {"etc...":"etc..."}}]'
```
#### Whitelisted library information
```python
#----------------------------------------------------------#
# Whitelisted libraries with corresponding user keys(s)
# These libraries are typically not searched for media items to delete
# Chosen during setup
#----------------------------------------------------------#
user_wl_libs='[{"userid": "abcdef0123456789abcdef0123456789", "username": "user1", "#": {"libid": "ffeeddccbbaa99887766554433221100", "collectiontype": "uvw", "networkpath": "smb://some/netpath/2", "path": "/some/path/2"}, "#": {"libid": "998877665544332211ffeeddccbbaa", "collectiontype": "xyz", "networkpath": "smb://some/netpath/3", "path": "/some/path/3"}}, {"etc...": "etc...", "#": {"etc...":"etc..."}}]'
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
#### Amount of RAM used for caching API requests
```python
#----------------------------------------------------------#
# API cache maximum size
# To keep the script running efficiently we do not want to send the
#  same requests to the server repeatedly
# If any single data entry is larger than the cache size, that data entry
#  will not be cached
# 0.1MB of cache is better than 0MB of cache
# Recommend setting DEBUG=1 to print the cache stats to determine the
#  best cache settings (i.e. size, fallback behavior, and last accessed time)
#
# MegaByte Sizing Reference
#  1MB = 1048576 Bytes
#  1000MB = 1GB
#  10000MB = 10GB
#
#  0 - Disable cache
#  1-10000 - Size of cache in megabytes (MB)
#  (10 : default)
#----------------------------------------------------------#
api_query_cache_size=10
```
#### Fallback cached item removal behavior when no entry is old enough
```python
#----------------------------------------------------------#
# API cache fallback behavior
# By default the script is a hybrid LFU/LRU RAM Cache
#
# 1.First the cache is filled
# 2.Once full the cache uses api_query_cache_last_accessed_time to
#    establish a minimum age an entry has to be for removal
# 3.Then the oldest entry meeting the minimum age (from step 2) with
#    the lowest number of hits (reads) is removed
# 4.If no entrys meet the minimum age or all have the same number of
#    cache hits (reads); api_query_cache_fallback_behavior is used
# Recommend setting DEBUG=1 to print the cache stats to determine the
#  best cache settings (i.e. size, fallback behavior, and last accessed time)
#
# Fallback To
#  'FIFO' - First In First Out (first entry is removed)
#  'LFU' - Least Frequently Used (first entry with the lowest number of hits is removed)
#  'LRU' - Least Recently Used (first entry with the oldest access time is removed)
#  (LRU : default)
#----------------------------------------------------------#
api_query_cache_fallback_behavior='LRU'
```
#### Miniumum amount of time a cached entry could live
```python
#----------------------------------------------------------#
# API cache entry minium age
#
# Once full the cache uses api_query_cache_last_accessed_time to
#  establish a minimum age an entry has to be for removal
#
# Bigger is NOT always better here. The older an entry is allowed
#  to be, the less entries can be removed from cache when it is full.
#  When this happens the script will not be able to find an entry that
#  satisfies LRU/LFU and will use api_query_cache_fallback_behavior
#  until there is enough space in cache for the newest entry.
# Of course setting a bigger cache size means needing to remove less
#  cache entries.
# Increase api_query_cache_size before increasing this api_query_cache_last_accessed_time
# Recommend setting DEBUG=1 to print the cache stats to determine the
#  best cache settings (i.e. size, fallback behavior, and last accessed time)
#
#  0-600000 - Minimum cached entry age for removal in milliseconds (ms)
#  (200 : default)
#----------------------------------------------------------#
api_query_cache_last_accessed_time=200
```
#### DEBUG
```python
#----------------------------------------------------------#
# Must be an integer value
#  Debug log file save to: /the/script/directory/mumc_DEBUG.log
#  The debug log file can be large (i.e. 10s to 100s of MBytes)
#  Recommend only enabling DEBUG when necessary
#   1 - Level 1 debug messaging enabled
#   2 - Level 2 debug messaging enabled
#   3 - Level 3 debug messaging enabled
#   4 - Level 4 debug messaging enabled
# (0 : default)
#----------------------------------------------------------#
DEBUG=0
```

# Delete Or Keep Priorities Of A Media Item

1. **Favorites** (Highest Priority)
   - _Media item will follow Action (W) in favorited\_behavior\_\*_
      - Whitetags ignored
      - Blacktags ignored
      - Whitelists ignored
      - Blacklists ignored
2. **Whitetags**
   - _Media item will follow Action (W) in whitetagged\_behavior\_\*_
      - Blacktags ignored
      - Whitelists ignored
      - Blacklists ignored
3. **Blacktags**
   - _Media item will follow Action (W) in blacktagged\_behavior\_\*_
      - Whitelists ignored
      - Blacklists ignored
4. **Whitelists**
   - _Media item will follow Action (W) in whitelisted\_behavior\_\*_
      - Blacklists ignored
5. **Blacklists** (Lowest priority)
   - _Media item will follow Action (W) in blacklisted\_behavior\_\*_

# Blacklisting vs Whitelisting
* [Explaination and examples.](https://github.com/terrelsa13/MUMC/issues/27#issue-1293645665)

# Blacktagging vs Whitetagging
* [Explaination and examples.](https://github.com/terrelsa13/MUMC/issues/16#issue-1205993797)

# Minimum Number of Episodes vs Minimum Number of Played Episodes
* [Explaination and examples.](https://github.com/terrelsa13/MUMC/issues/21#issue-1258905586)

# Library Matching By Id, By Path, or By Network Path
* [Explaination and examples.](https://github.com/terrelsa13/MUMC/issues/18#issue-1217953189)

# Known Limitations
* When importing played states from Trakt the ```days since played``` shown in the console output will not show the correct value.
  - This is an issue with the ```last played date``` not being filled in when played states are imported from Trakt to Emby/Jellyfin.
  - The script is able to compensate for this using the [```*_set_missing_last_played_date```](https://github.com/terrelsa13/MUMC/#add-lastplayeddate-for-media-items-without-it) options.

# Requirements
* Linux, Windows, or MAC
* Python 3.11
   - Other versions of python 3.x will likely work; but are not supported
   - Python 2.x or earlier are not supported and will not work
* python-dateutil **must be installed**
* Emby/Jellyfin need to have OS level permissions on Linux machines to delete media items: [Read This Post](https://github.com/terrelsa13/MUMC/issues/28#issue-1293649223)

# First Run (Debian, Ubuntu, and Linux Mint)
* Install Python version mentioned in the 'Requirements' section above
  - If this version of Python is not already installed do NOT overwrite the defaul OS Python version
  - Instead use the link below to create an alternate install of Python
    - [Python 3.7 example](https://tecadmin.net/install-python-3-7-on-ubuntu-linuxmint/) (These instructions will apply to any version of Python.)
* Verify your Python verison
   - $```python3.11 -V```
* Next install the python-dateutil module with the following commands:
   - $```sudo apt-get upgrade -y```
   - $```sudo apt-get install python3-pip -y```
   - $```pip3 install -U pip```
   - $```pip3.11 install python-dateutil```
* **\*OPTIONAL\*** Use a text editor to update the mumc_config_defaults.py file with desired default values
   - $```nano /path/to/mumc_config_defaults.py```
* Make the script executable
   - $```chmod +x /path/to/mumc.py```
* Run the script
   - $```/path/to/python3.x /path/to/mumc.py```
* First time the script is run, it will walk through creating the mumc_config.py file
* If you get the below python error the python-dateutil module was not properly installed
   - ```ModuleNotFoundError: No module named 'dateutil' python-dateutil```

# First Run (Windows)
* Download the latest [MUMC.zip](https://github.com/terrelsa13/MUMC/releases/latest)
* Move the MUMC.zip to your user's directory (below path assumes your username is Zoomies)
  - ```C:\Users\Zoomies```
* Extract MUMC.zip
  - There should now be a MUMC folder
  - ```C:\Users\Zoomies\MUMC```
* Next go to https://www.python.org/ and install the python version shown in the [Requirements section](https://github.com/terrelsa13/MUMC#requirements)
* After python is installed; open a command window
  - Select: The Start Menu
  - Type: ```cmd```
  - Press: ```Enter``` key
* Using the command window, install the python-dateutil module
  - Type: ```pip install python-dateutil```
* After the python-dateutil module is installed keep the command window open
* Change current working directory of the command window to the ```C:\Users\Zoomies\MUMC``` folder using the command below
  - Type: cd ```C:\Users\Zoomies\MUMC```
* Now run the script in the command window using the command below
  - Type: ```python mumc.py```
  - Follow the script prompts
    - First time the script is run, it will walk through creating the ```mumc_config.py``` file in ```C:\Users\Zoomies\MUMC``` folder
* After the ```mumc_config.py``` file is created it can be edited in a text editor (e.g. Notepad, Notepad++, Visual Studio, UltraEdit, etc...)
* Once ```mumc_config.py``` is configured as desired, run the script again using the same command from above
  - Type: ```python mumc.py```

# First Run (Other Operating Systems)
* Consult your favorite search engine

# Schedule To Run Using Crontab (Debian, Ubuntu, and Linux Mint)
* Below cron entry runs ```mumc.py``` everyday at 00:00hrs (aka 12:00am)
   - $```0 0 * * * /usr/local/bin/python3.11 /opt/mumc/mumc.py```
* Below cron entry runs ```mumc.py``` every Monday at 01:23hrs (aka 1:23)am and saves the output to a file called mumc.log in the /var/log/ directory
   - $```23 1 * * 1 /usr/local/bin/python3.11 /opt/mumc/mumc.py > /var/log/mumc.log 2>&1```

# Schedule To Run (Windows)
* Consult your favorite search engine for a Windows task scheduler

# Schedule To Run (Other Operating Systems)
* Consult your favorite search engine

# Donation
If you find MUMC useful and would like to show support, please consider the option below.

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/donate?hosted_button_id=4CFFHMJV3H4M2)
