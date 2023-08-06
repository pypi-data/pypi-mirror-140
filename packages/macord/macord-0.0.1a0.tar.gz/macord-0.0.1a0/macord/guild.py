from typing import Dict, List
from .user import *

class RoleTags:
    def __init__(self, json: Dict) -> None:
        if json == None:
            self = None
            return
        self.bot_id: str = json.get("bot_id", None)
        self.integration_id: str = json.get("integration_id", None)
        self.premium_subscriber = None

class Role:
    def __init__(self, json: Dict) -> None:
        if json == None:
            self = None
            return
        self.id: str = json["id"]
        self.name: str = json["name"]
        self.color: int = json["color"]
        self.hoist: bool = json["hoist"]
        self.icon: str = json.get("icon", None)
        self.unicode_emoji: str = json.get("unicode_emoji", None)
        self.position: int = json["position"]
        self.permissions: str = json["permissions"]
        self.managed: bool = json["managed"]
        self.mentionable: bool = json["mentionable"]
        self.tags: RoleTags = RoleTags(json.get("unicode_emoji"))

class GuildMember:
    def __init__(self, json: Dict) -> None:
        if json == None:
            self = None
            return
        self.user: User = json.get("user", None)
        if not self.user is None:
            self.user = User(self.user)
        self.nick: str = json.get("nick", None)
        self.avatar: str = json.get("avatar", None)
        self.roles: List[str] = json["roles"]
        self.joined_at: str = json["joined_at"]
        self.premium_since: str = json.get("premium_since", None)
        self.deaf: bool = json["deaf"]
        self.mute: bool = json["mute"]
        self.pending: bool = json.get("pending", None)
        self.permissions: str = json.get("permissions", None)
        self.communication_disabled_until: str = json.get("communication_disabled_until", None)