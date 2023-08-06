import enum
from typing import Dict

class UserFlags(enum.IntFlag):
    NONE = 0
    STAFF = 1 << 0
    PARTNER = 1 << 1
    HYPESQUAD = 1 << 2
    BUG_HUNTER_LEVEL_1 = 1 << 3
    HYPESQUAD_ONLINE_HOUSE_1 = 1 << 6
    HYPESQUAD_ONLINE_HOUSE_2 = 1 << 7
    HYPESQUAD_ONLINE_HOUSE_3 = 1 << 8
    PREMIUM_EARLY_SUPPORTER	= 1 << 9
    TEAM_PSEUDO_USER = 1 << 10
    BUG_HUNTER_LEVEL_2 = 1 << 14
    VERIFIED_BOT = 1 << 16
    VERIFIED_DEVELOPER = 1 << 17
    CERTIFIED_MODERATOR = 1 << 18
    BOT_HTTP_INTERACTIONS = 1 << 19

class UserPremiumTypes(enum.Enum):
    NONE = 0
    NITRO_CLASSIC = 1
    NITRO = 2

class User:
    def __init__(self, json: Dict) -> None:
        if json == None:
            self = None
            return
        self.id: str = json["id"]
        self.username: str = json["username"]
        self.discriminator: str = json["discriminator"]
        self.avatar: str = json["avatar"]
        self.bot: bool = json.get("bot", None)
        self.system: bool = json.get("system", None)
        self.mfa_enabled: bool = json.get("mfa_enabled", None)
        self.banner: str = json.get("banner", None)
        self.accent_color: int = json.get("accent_color", None)
        self.locale: str = json.get("locale", None)
        self.verified: bool = json.get("verified", None)
        self.email: str = json.get("email", None)
        self.flags: UserFlags = json.get("flags", None)
        if not self.flags is None:
            self.flags = UserFlags(self.flags)
        self.premium_type: UserPremiumTypes = json.get("premium_type", None)
        if not self.premium_type is None:
            self.premium_type = UserPremiumTypes(self.premium_type)
        self.public_flags: UserFlags = json.get("public_flags", None)
        if not self.public_flags is None:
            self.public_flags = UserFlags(self.public_flags)