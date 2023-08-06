import enum
from typing import Dict, List
from .user import *

class ChannelTypes(enum.Enum):
    GUILD_TEXT = 0
    DM = 1
    GUILD_VOICE = 2
    GROUP_DM = 3
    GUILD_CATEGORY = 4
    GUILD_NEWS = 5
    GUILD_STORE = 6
    GUILD_NEWS_THREAD = 10
    GUILD_PUBLIC_THREAD = 11
    GUILD_PRIVATE_THREAD = 12
    GUILD_STAGE_VOICE = 13

class Channel:
    def __init__(self, json: Dict) -> None:
        if json == None:
            self = None
            return
        self.id: str = json["id"]
        self.type: ChannelTypes = ChannelTypes(json["type"])
        self.guild_id: str = json.get("guild_id", None)
        self.position: int = json.get("position", None)
        self.permission_overwrites: List[Overwrite] = []
        permission_overwrites: List[Dict] = json.get("permission_overwrites", None)
        if not permission_overwrites is None:
            for permission_overwrite in permission_overwrites:
                self.permission_overwrites.append(Overwrite(permission_overwrite))
        self.name: str = json.get("name", None)
        self.topic: str = json.get("topic", None)
        self.nsfw: bool = json.get("nsfw", None)
        self.last_message_id: str = json.get("last_message_id", None)
        self.bitrate: int = json.get("bitrate", None)
        self.user_limit: int = json.get("user_limit", None)
        self.rate_limit_per_user: int = json.get("rate_limit_per_user", None)
        self.recipients: List[User] = []
        recipients: List[Dict] = json.get("recipients", None)
        if not recipients is None:
            for recipient in recipients:
                self.recipients.append(User(recipient))
        self.icon: str = json.get("icon", None)
        self.owner_id: str = json.get("owner_id", None)
        self.application_id: str = json.get("application_id", None)
        self.parent_id: str = json.get("parent_id", None)
        self.last_pin_timestamp: str = json.get("last_pin_timestamp", None)
        self.rtc_region: str = json.get("rtc_region", None)
        self.video_quality_mode: int = json.get("video_quality_mode", None)
        self.message_count: int = json.get("message_count", None)
        self.member_count: int = json.get("member_count", None)
        self.thread_metadata: ThreadMetadata = json.get("thread_metadata", None)
        if not self.thread_metadata is None:
            self.thread_metadata = ThreadMetadata(self.thread_metadata)
        self.member: ThreadMember = json.get("member", None)
        if not self.member is None:
            self.member = ThreadMember(self.member)
        self.default_auto_archive_duration: int = json.get("default_auto_archive_duration", None)
        self.permissions: str = json.get("permissions", None)

class ChannelMention:
    def __init__(self, json: Dict) -> None:
        if json == None:
            self = None
            return
        self.id: str = json["id"]
        self.guild_id: str = json["guild_id"]
        self.type: ChannelTypes = ChannelTypes(json["type"])
        self.name: str = json["name"]

class OverwriteType(enum.Enum):
    ROLE = 0
    MEMBER = 1

class Overwrite:
    def __init__(self, json: Dict) -> None:
        if json == None:
            self = None
            return
        self.id: str = json["id"]
        self.type: OverwriteType = OverwriteType(json["type"])
        self.allow: str = json["allow"]
        self.deny: str = json["deny"]

class ThreadMetadata:
    def __init__(self, json: Dict) -> None:
        if json == None:
            self = None
            return
        self.archived: bool = json["archived"]
        self.auto_archive_duration: int = json["auto_archive_duration"]
        self.archive_timestamp: str = json["archive_timestamp"]
        self.locked: bool = json["locked"]
        self.invitable: bool = json.get("invitable", None)
        self.create_timestamp: str = json.get("create_timestamp", None)

class ThreadMember:
    def __init__(self, json: Dict) -> None:
        if json == None:
            self = None
            return
        self.id: str = json.get("id", None)
        self.user_id: str = json.get("user_id", None)
        self.join_timestamp: str = json.get("join_timestamp", None)
        self.flags: int = json.get("flags", None)