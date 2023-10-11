from typing import List, Optional, Dict
from enum import Enum


class APIControls:
    attempts: int
    item_limit: int

    def __init__(self, attempts: int, item_limit: int) -> None:
        self.attempts = attempts
        self.item_limit = item_limit


class Behavior:
    list: str
    matching: str

    def __init__(self, list: str, matching: str) -> None:
        self.list = list
        self.matching = matching


class Cache:
    size: int
    fallback_behavior: str
    last_accessed_time: int

    def __init__(self, size: int, fallback_behavior: str, last_accessed_time: int) -> None:
        self.size = size
        self.fallback_behavior = fallback_behavior
        self.last_accessed_time = last_accessed_time


class Server:
    brand: str
    url: str
    auth_key: str

    def __init__(self, brand: str, url: str, auth_key: str) -> None:
        self.brand = brand
        self.url = url
        self.auth_key = auth_key


class BWlistElement:
    lib_id: str
    lib_enabled: bool
    collection_type: str
    path: str
    network_path: str

    def __init__(self, lib_id: str, collection_type: str, path: str, network_path: str, lib_enabled: bool) -> None:
        self.lib_id = lib_id
        self.collection_type = collection_type
        self.path = path
        self.network_path = network_path
        self.lib_enabled = lib_enabled


class User:
    user_id: str
    user_name: str
    whitelist: List[BWlistElement]
    blacklist: List[BWlistElement]

    def __init__(self, user_id: str, user_name: str, whitelist: List[BWlistElement], blacklist: List[BWlistElement]) -> None:
        self.user_id = user_id
        self.user_name = user_name
        self.whitelist = whitelist
        self.blacklist = blacklist


class AdminSettings:
    server: Server
    behavior: Behavior
    users: List[User]
    api_controls: APIControls
    cache: Cache

    def __init__(self, server: Server, behavior: Behavior, users: List[User], api_controls: APIControls, cache: Cache) -> None:
        self.server = server
        self.behavior = behavior
        self.users = users
        self.api_controls = api_controls
        self.cache = cache


class Action(Enum):
    DELETE = "delete"
    KEEP = "keep"


class Conditional(Enum):
    ALL = "all"
    ANY = "any"
    ALL_ALL = "all_all"
    ANY_ANY = "any_any"
    ANY_ALL = "any_all"
    ALL_ANY = "all_any"
    ANY_PLAYED = "any_played"
    ALL_PLAYED = "all_played"
    ANY_CREATED = "any created"
    ALL_CREATED = "all_created"
    IGNORE = "ignore"


class Blacklisted:
    action: Action
    user_conditional: Conditional
    played_conditional: Conditional
    action_control: int
    tags: Optional[List[str]]
    advanced: Optional[Dict[str, int]]

    def __init__(self, action: Action, user_conditional: Conditional, played_conditional: Conditional, action_control: int, tags: Optional[List[str]], advanced: Optional[Dict[str, int]]) -> None:
        self.action = action
        self.user_conditional = user_conditional
        self.played_conditional = played_conditional
        self.action_control = action_control
        self.tags = tags
        self.advanced = advanced


class BehavioralStatementsMedia:
    favorited: Blacklisted
    whitetagged: Blacklisted
    blacktagged: Blacklisted
    whitelisted: Blacklisted
    blacklisted: Blacklisted

    def __init__(self, favorited: Blacklisted, whitetagged: Blacklisted, blacktagged: Blacklisted, whitelisted: Blacklisted, blacklisted: Blacklisted) -> None:
        self.favorited = favorited
        self.whitetagged = whitetagged
        self.blacktagged = blacktagged
        self.whitelisted = whitelisted
        self.blacklisted = blacklisted


class BehavioralStatements:
    movie: BehavioralStatementsMedia
    episode: BehavioralStatementsMedia
    audio: BehavioralStatementsMedia
    audiobook: Optional[BehavioralStatementsMedia]

    def __init__(self, movie: BehavioralStatementsMedia, episode: BehavioralStatementsMedia, audio: BehavioralStatementsMedia, audiobook: Optional[BehavioralStatementsMedia]) -> None:
        self.movie = movie
        self.episode = episode
        self.audio = audio
        self.audiobook = audiobook


class Background:
    color: str

    def __init__(self, color: str) -> None:
        self.color = color


class Font:
    color: str
    style: str

    def __init__(self, color: str, style: str) -> None:
        self.color = color
        self.style = style


class Formatting:
    font: Font
    background: Background

    def __init__(self, font: Font, background: Background) -> None:
        self.font = font
        self.background = background


class Delete:
    show: bool
    formatting: Formatting

    def __init__(self, show: bool, formatting: Formatting) -> None:
        self.show = show
        self.formatting = formatting


class ConsoleControlsMedia:
    delete: Delete
    keep: Delete
    post_processing: Delete
    summary: Delete

    def __init__(self, delete: Delete, keep: Delete, post_processing: Delete, summary: Delete) -> None:
        self.delete = delete
        self.keep = keep
        self.post_processing = post_processing
        self.summary = summary


class Footers:
    script: Delete

    def __init__(self, script: Delete) -> None:
        self.script = script


class Headers:
    script: Delete
    user: Delete
    summary: Delete

    def __init__(self, script: Delete, user: Delete, summary: Delete) -> None:
        self.script = script
        self.user = user
        self.summary = summary


class ConsoleControls:
    headers: Headers
    footers: Footers
    warnings: Footers
    movie: ConsoleControlsMedia
    episode: ConsoleControlsMedia
    audio: ConsoleControlsMedia
    audiobook: Optional[ConsoleControlsMedia]

    def __init__(self, headers: Headers, footers: Footers, warnings: Footers, movie: ConsoleControlsMedia, episode: ConsoleControlsMedia, audio: ConsoleControlsMedia, audiobook: Optional[ConsoleControlsMedia]) -> None:
        self.headers = headers
        self.footers = footers
        self.warnings = warnings
        self.movie = movie
        self.episode = episode
        self.audio = audio
        self.audiobook = audiobook


class EpisodeControl:
    minimum_episodes: int
    minimum_played_episodes: int
    minimum_episodes_behavior: str

    def __init__(self, minimum_episodes: int, minimum_played_episodes: int, minimum_episodes_behavior: str) -> None:
        self.minimum_episodes = minimum_episodes
        self.minimum_played_episodes = minimum_played_episodes
        self.minimum_episodes_behavior = minimum_episodes_behavior


class SetMissingLastPlayedDate:
    movie: bool
    episode: bool
    audio: bool
    audiobook: bool

    def __init__(self, movie: bool, episode: bool, audio: bool, audiobook: bool) -> None:
        self.movie = movie
        self.episode = episode
        self.audio = audio
        self.audiobook = audiobook


class TraktFix:
    set_missing_last_played_date: SetMissingLastPlayedDate

    def __init__(self, set_missing_last_played_date: SetMissingLastPlayedDate) -> None:
        self.set_missing_last_played_date = set_missing_last_played_date


class AdvancedSettings:
    behavioral_statements: BehavioralStatements
    whitetags: List[str]
    blacktags: List[str]
    episode_control: EpisodeControl
    trakt_fix: TraktFix
    console_controls: ConsoleControls
    update_config: bool
    remove_files: bool

    def __init__(self, behavioral_statements: BehavioralStatements, whitetags: List[str], blacktags: List[str], episode_control: EpisodeControl, trakt_fix: TraktFix, console_controls: ConsoleControls, update_config: bool, remove_files: bool) -> None:
        self.behavioral_statements = behavioral_statements
        self.whitetags = whitetags
        self.blacktags = blacktags
        self.episode_control = episode_control
        self.trakt_fix = trakt_fix
        self.console_controls = console_controls
        self.update_config = update_config
        self.remove_files = remove_files


class FilterType:
    condition_days: int
    count_equality: str
    count: int
    behavioral_control: Optional[bool]

    def __init__(self, condition_days: int, count_equality: str, count: int, behavioral_control: Optional[bool]) -> None:
        self.condition_days = condition_days
        self.count_equality = count_equality
        self.count = count
        self.behavioral_control = behavioral_control


class FilterStatementsMedia:
    played: FilterType
    created: FilterType

    def __init__(self, played: FilterType, created: FilterType) -> None:
        self.played = played
        self.created = created


class FilterStatements:
    movie: FilterStatementsMedia
    episode: FilterStatementsMedia
    audio: FilterStatementsMedia
    audiobook: Optional[FilterStatementsMedia]

    def __init__(self, movie: FilterStatementsMedia, episode: FilterStatementsMedia, audio: FilterStatementsMedia, audiobook: Optional[FilterStatementsMedia]) -> None:
        self.movie = movie
        self.episode = episode
        self.audio = audio
        self.audiobook = audiobook


class BasicSettings:
    filter_statements: FilterStatements

    def __init__(self, filter_statements: FilterStatements) -> None:
        self.filter_statements = filter_statements


class yaml_mapper:
    version: Optional[str]
    basic_settings: Optional[BasicSettings]
    advanced_settings: Optional[AdvancedSettings]
    admin_settings: Optional[AdminSettings]
    debug: int

    def __init__(self, version: Optional[str], basic_settings: Optional[BasicSettings], advanced_settings: Optional[AdvancedSettings], admin_settings: Optional[AdminSettings], debug: Optional[int]) -> None:
        self.version = version
        self.basic_settings = basic_settings
        self.advanced_settings = advanced_settings
        self.admin_settings = admin_settings
        self.debug = debug
