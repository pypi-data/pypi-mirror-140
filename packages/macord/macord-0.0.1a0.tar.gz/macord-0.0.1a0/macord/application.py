from typing import Dict, List
from .user import *

class ApplicationFlags(enum.IntFlag):
    GATEWAY_PRESENCE = 1 << 12
    GATEWAY_PRESENCE_LIMITED = 1 << 13
    GATEWAY_GUILD_MEMBERS = 1 << 14
    GATEWAY_GUILD_MEMBERS_LIMITED = 1 << 15
    VERIFICATION_PENDING_GUILD_LIMIT = 1 << 16
    EMBEDDED = 1 << 17
    GATEWAY_MESSAGE_CONTENT = 1 << 18
    GATEWAY_MESSAGE_CONTENT_LIMITED = 1 << 19

class Application:
    def __init__(self, json: Dict) -> None:
        if json is None:
            self = None
            return
        self.id: str = json["id"]
        self.name: str = json["name"]
        self.icon: str = json["icon"]
        self.description: str = json["description"]
        self.rpc_origins: List[str] = json.get("rpc_origins", None)
        self.bot_public: bool = json["bot_public"]
        self.bot_require_code_grant: bool = json["bot_require_code_grant"]
        self.terms_of_service_url: str = json.get("terms_of_service_url", None)
        self.privacy_policy_url: str = json.get("privacy_policy_url", None)
        self.owner: User = json.get("owner", None)
        if not self.owner is None:
            self.owner = User(self.owner)
        self.summary: str = json["summary"]
        self.verify_key: str = json["verify_key"]
        self.team: Team = Team(json["team"])
        self.guild_id: str = json.get("guild_id", None)
        self.primary_sku_id: str = json.get("primary_sku_id", None)
        self.slug: str = json.get("slug", None)
        self.cover_image: str = json.get("cover_image", None)
        self.flags: ApplicationFlags = json.get("flags", None)
        if not self.flags is None:
            self.flags = ApplicationFlags(self.flags)

class Team:
    def __init__(self, json: Dict) -> None:
        if json is None:
            self = None
            return
        self.icon: str = json.get("icon", None)
        self.id: str = json["id"]
        self.members: List[TeamMember] = []
        members: List[Dict] = json["members"]
        for member in members:
            self.members.append(TeamMember(member))
        self.name: str = json["name"]
        self.owner_user_id: str = json["owner_user_id"]

class TeamMember:
    def __init__(self, json: Dict) -> None:
        if json is None:
            self = None
            return
        self.membership_state: int = json["membership_state"]
        self.permissions: List[str] = json["permissions"]
        self.team_id: str = json["team_id"]
        self.user: User = User(json["user"])