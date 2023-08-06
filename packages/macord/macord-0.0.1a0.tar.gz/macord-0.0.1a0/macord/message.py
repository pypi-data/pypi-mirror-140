from typing import Any, Dict, Union
from .guild import *
from .channel import *
from .application import *

class MessageType(enum.Enum):
    DEFAULT = 0
    RECIPIENT_ADD = 1
    RECIPIENT_REMOVE = 2
    CALL = 3
    CHANNEL_NAME_CHANGE = 4
    CHANNEL_ICON_CHANGE = 5
    CHANNEL_PINNED_MESSAGE = 6
    GUILD_MEMBER_JOIN = 7
    USER_PREMIUM_GUILD_SUBSCRIPTION = 8
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_1 = 9
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_2 = 10
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_3 = 11
    CHANNEL_FOLLOW_ADD = 12
    GUILD_DISCOVERY_DISQUALIFIED = 14
    GUILD_DISCOVERY_REQUALIFIED = 15
    GUILD_DISCOVERY_GRACE_PERIOD_INITIAL_WARNING = 16
    GUILD_DISCOVERY_GRACE_PERIOD_FINAL_WARNING = 17
    THREAD_CREATED = 18
    REPLY = 19
    CHAT_INPUT_COMMAND = 20
    THREAD_STARTER_MESSAGE = 21
    GUILD_INVITE_REMINDER = 22
    CONTEXT_MENU_COMMAND = 23

class MessageFlags(enum.IntFlag):
    CROSSPOSTED = 1 << 0
    IS_CROSSPOST = 1 << 1
    SUPPRESS_EMBEDS = 1 << 2
    SOURCE_MESSAGE_DELETED = 1 << 3
    URGENT = 1 << 4
    HAS_THREAD = 1 << 5
    EPHEMERAL = 1 << 6
    LOADING = 1 << 7
    FAILED_TO_MENTION_SOME_ROLES_IN_THREAD = 1 << 8

class Message:
    def __init__(self, json: Dict):
        if json == None:
            self = None
            return
        self.id: str = json["id"]
        self.channel_id: str = json["channel_id"]
        self.guild_id: str = json.get("guild_id", None)
        self.author: User = User(json["author"])
        self.member: GuildMember = json.get("member", None)
        if not self.member is None:
            self.member = GuildMember(self.member)
        self.content: str = json["content"]
        self.timestamp: str = json["timestamp"]
        self.edited_timestamp: str = json["edited_timestamp"]
        self.tts: bool = json["tts"]
        self.mention_everyone: bool = json["mention_everyone"]
        self.mentions: List[MentionUser] = []
        mentions: List[Dict] = json["mentions"]
        for mention in mentions:
            self.mentions.append(MentionUser(mention))
        self.mention_roles: List[str] = json["mention_roles"]
        self.mention_channels: List[ChannelMention] = []
        mention_channels: List[Dict] = json.get("mention_channels", None)
        if not mention_channels is None:
            for mention_channel in mention_channels:
                self.mention_channels.append(ChannelMention(mention_channel))
        self.attachments: List[Attachment] = []
        attachments: List[Dict] = json["attachments"]
        for attachment in attachments:
            self.attachments.append(Attachment(attachment))
        self.embeds: List[Embed] = []
        embeds: List[Embed] = json["embeds"]
        for embed in embeds:
            self.embeds.append(Embed(embed))
        self.reactions: List[Reaction] = []
        reactions: List[Reaction] = json.get("reactions", None)
        if not reactions is None:
            for reaction in reactions:
                self.reactions.append(Reaction(reaction))
        self.nonce: Union[int, str] = json.get("nonce", None)
        self.pinned: bool = json["pinned"]
        self.webhook_id: str = json.get("webhook_id", None)
        self.type: MessageType = MessageType(json["type"])
        self.activity: MessageActivity = json.get("activity", None)
        if not self.activity is None:
            self.activity = MessageActivity(self.activity)
        self.application: Application = json.get("application", None)
        if not self.application is None:
            self.application = Application(self.application)
        self.application_id: str = json.get("application_id", None)
        self.message_reference: MessageReference = json.get("message_reference", None)
        if not self.message_reference is None:
            self.message_reference = MessageReference(self.message_reference)
        self.flags: MessageFlags = json.get("flags", None)
        if not self.flags is None:
            self.flags = MessageFlags(self.flags)
        self.referenced_message: Message = json.get("referenced_message", None)
        if not self.referenced_message is None:
            self.referenced_message = Message(self.referenced_message)
        self.interaction: MessageInteraction = json.get("interaction", None)
        if not self.interaction is None:
            self.interaction = MessageInteraction(self.interaction)
        self.thread: Channel = json.get("thread", None)
        if not self.thread is None:
            self.thread = Channel(self.thread)
        self.sticker_items: List[StickerItem] = []
        sticker_items: List[Dict] = json.get("sticker_items", None)
        if not sticker_items is None:
            for sticker_item in sticker_items:
                self.sticker_items.append(StickerItem(sticker_item))
        self.stickers: List[Sticker] = []
        stickers: List[Dict] = json.get("stickers", None)
        if not stickers is None:
            for sticker in stickers:
                self.stickers.append(Sticker(sticker))

class MentionUser:
    def __init__(self, json: Dict) -> None:
        if json == None:
            self = None
            return
        self.user: User = json.get("user", None)
        if not self.user is None:
            self.user = User(self.user)
        self.nick: str = json.get("nick", None)
        self.avatar: str = json.get("avatar", None)
        self.roles: List[str] = json.get("roles", None)
        self.joined_at: str = json.get("joined_at")
        self.premium_since: str = json.get("premium_since", None)
        self.deaf: bool = json.get("deaf")
        self.mute: bool = json.get("mute")
        self.pending: bool = json.get("pending", None)
        self.permissions: str = json.get("permissions", None)
        self.communication_disabled_until: str = json.get("communication_disabled_until", None)
        self.id: str = json["id"]
        self.username: str = json["username"]
        self.discriminator: str = json["discriminator"]
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

class Attachment:
    def __init__(self, json: Dict) -> None:
        if json == None:
            self = None
            return
        self.id: str = json["id"]
        self.name: str = json["filename"]
        self.description: str = json.get("description", None)
        self.content_type: str = json.get("content_type", None)
        self.size: int = json["size"]
        self.url: str = json["url"]
        self.proxy_url: str = json["proxy_url"]
        self.height: int = json.get("height", None)
        self.width: int = json.get("width", None)
        self.ephemeral: bool = json.get("ephemeral", None)
    def to_json(self) -> Dict[str, Any]:
        result = {"id": self.id, "name": self.name, "size": self.size, "url": self.url}

        if self.description != None and type(self.description) == str:
            result["description"] = self.description
        if self.content_type != None and type(self.content_type) == str:
            result["content_type"] = self.content_type
        if self.proxy_url != None and type(self.proxy_url) == str:
            result["proxy_url"] = self.proxy_url
        if self.height != None and type(self.height) == int:
            result["height"] = self.height
        if self.width != None and type(self.width) == int:
            result["width"] = self.width
        if self.ephemeral != None and type(self.ephemeral) == bool:
            result["ephemeral"] = self.ephemeral

        return result

class EmbedType(enum.Enum):
    RICH = "rich"
    IMAGE = "image"
    VIDEO = "video"
    GIF = "gifv"
    ARTICLE = "article"
    LINK = "link"

class Embed:
    def __init__(self, json: Dict) -> None:
        if json == None:
            self = None
            return
        self.title: str = json.get("title", None)
        self.type: EmbedType = json.get("type", None)
        if not self.type is None:
            self.type = EmbedType(self.type)
        self.description: str = json.get("description", None)
        self.url: str = json.get("url", None)
        self.timestamp: str = json.get("timestamp", None)
        self.color: int = json.get("color", None)
        self.footer: EmbedFooter = json.get("footer", None)
        if not self.footer is None:
            self.footer = EmbedFooter(self.footer)
        self.image: EmbedImage = json.get("image", None)
        if not self.image is None:
            self.image = EmbedImage(self.image)
        self.thumbnail: EmbedThumbnail = json.get("thumbnail", None)
        if not self.thumbnail is None:
            self.thumbnail = EmbedThumbnail(self.thumbnail)
        self.video: EmbedVideo = json.get("video", None)
        if not self.video is None:
            self.video = EmbedVideo(self.video)
        self.provider: EmbedProvider = json.get("provider", None)
        if not self.provider is None:
            self.provider = EmbedProvider(self.provider)
        self.author: EmbedAuthor = json.get("author", None)
        if not self.author is None:
            self.author = EmbedAuthor(self.author)
        self.fields: List[EmbedFiled] = []
        fields: List[Dict] = json.get("fields", None)
        if not fields is None:
            for field in fields:
                self.fields.append(EmbedFiled(field))
    def to_json(self) -> Dict[str, Any]:
        result = {}
        if self.title != None and type(self.title) == str:
            result["title"] = self.title
        if self.type != None and type(self.type) == EmbedType:
            result["type"] = self.type
        if self.description != None and type(self.description) == str:
            result["description"] = self.description
        if self.url != None and type(self.url) == str:
            result["url"] = self.url
        if self.timestamp != None and type(self.timestamp) == str:
            result["timestamp"] = self.timestamp
        if self.color != None and type(self.color) == int:
            result["color"] = self.color
        if self.footer != None and type(self.footer) == EmbedFooter:
            result["footer"] = self.footer.to_json()
        if self.image != None and type(self.image) == EmbedImage:
            result["image"] = self.image.to_json()
        if self.thumbnail != None and type(self.thumbnail) == EmbedThumbnail:
            result["thumbnail"] = self.thumbnail.to_json()
        if self.video != None and type(self.video) == EmbedVideo:
            result["video"] = self.video.to_json()
        if self.provider != None and type(self.provider) == EmbedProvider:
            result["provider"] = self.provider.to_json()
        if self.author != None and type(self.author) == EmbedAuthor:
            result["author"] = self.author
        if self.fields != None:
            result["fields"] = []
            for field in self.fields:
                if type(field) == EmbedFiled:
                    result["fields"].append(field.to_json())

        return result

class EmbedFooter:
    def __init__(self, json: Dict) -> None:
        if json == None:
            self = None
            return
        self.text: str = json["text"]
        self.icon_url: str = json.get("icon_url", None)
        self.proxy_icon_url: str = json.get("proxy_icon_url", None)
    def to_json(self) -> Dict[str, Any]:
        result = {
            "text": self.text
        }
        if self.icon_url != None and type(self.icon_url) == str:
            result["icon_url"] = self.icon_url
        if self.proxy_icon_url != None and type(self.proxy_icon_url) == str:
            result["proxy_icon_url"] = self.proxy_icon_url
        return result

class EmbedImage:
    def __init__(self, json: Dict) -> None:
        if json == None:
            self = None
            return
        self.url: str = json["url"]
        self.proxy_url: str = json.get("proxy_url", None)
        self.width: int = json.get("width", None)
        self.height: int = json.get("height", None)
    def to_json(self) -> Dict[str, Any]:
        result = {
            "url": self.url
        }
        if self.proxy_url != None and type(self.proxy_url) == str:
            result["proxy_url"] = self.proxy_url
        if self.width != None and type(self.width) == int:
            result["width"] = self.width
        if self.height != None and type(self.height) == int:
            result["height"] = self.height
        return result

class EmbedThumbnail:
    def __init__(self, json: Dict) -> None:
        if json == None:
            self = None
            return
        self.url: str = json["url"]
        self.proxy_url: str = json.get("proxy_url", None)
        self.width: int = json.get("width", None)
        self.height: int = json.get("height", None)
    def to_json(self) -> Dict[str, Any]:
        result = {
            "url": self.url
        }
        if self.proxy_url != None and type(self.proxy_url) == str:
            result["proxy_url"] = self.proxy_url
        if self.width != None and type(self.width) == int:
            result["width"] = self.width
        if self.height != None and type(self.height) == int:
            result["height"] = self.height
        return result

class EmbedVideo:
    def __init__(self, json: Dict) -> None:
        if json == None:
            self = None
            return
        self.url: str = json["url"]
        self.proxy_url: str = json.get("proxy_url", None)
        self.width: int = json.get("width", None)
        self.height: int = json.get("height", None)
    def to_json(self) -> Dict[str, Any]:
        result = {
            "url": self.url
        }
        if self.proxy_url != None and type(self.proxy_url) == str:
            result["proxy_url"] = self.proxy_url
        if self.width != None and type(self.width) == int:
            result["width"] = self.width
        if self.height != None and type(self.height) == int:
            result["height"] = self.height
        return result

class EmbedProvider:
    def __init__(self, json: Dict) -> None:
        if json == None:
            self = None
            return
        self.name: str = json.get("name", None)
        self.url: str = json.get("url", None)
    def to_json(self) -> Dict[str, Any]:
        result = {}
        if self.name != None and type(self.name) == str:
            result["name"] = self.name
        if self.url != None and type(self.url) == str:
            result["url"] = self.url
        return result

class EmbedAuthor:
    def __init__(self, json: Dict) -> None:
        if json == None:
            self = None
            return
        self.name: str = json["name"]
        self.url: str = json.get("url", None)
        self.icon_url: str = json.get("icon_url", None)
        self.proxy_icon_url: str = json.get("proxy_icon_url", None)
    def to_json(self) -> Dict[str, Any]:
        result = {}
        if self.name != None and type(self.name) == str:
            result["name"] = self.name
        if self.url != None and type(self.url) == str:
            result["url"] = self.url
        if self.icon_url != None and type(self.icon_url) == str:
            result["icon_url"] = self.icon_url
        if self.proxy_icon_url != None and type(self.proxy_icon_url) == str:
            result["proxy_icon_url"] = self.proxy_icon_url
        return result

class EmbedFiled:
    def __init__(self, json: Dict) -> None:
        if json == None:
            self = None
            return
        self.name: str = json["name"]
        self.value: str = json["value"]
        self.inline: bool = json.get("inline", False)
    def to_json(self) -> Dict[str, Any]:
        result = {"name": self.name, "value": self.value}
        if self.inline != None and type(self.inline) == bool:
            result["inline"] = self.inline
        return result

class Emoji:
    def __init__(self, json: Dict) -> None:
        if json == None:
            self = None
            return
        self.id: str = json["id"]
        self.name: str = json["name"]
        self.roles: List[str] = json.get("roles", None)
        self.user: User = json.get("user", None)
        if not self.user is None:
            self.user = User(self.user)
        self.require_colons: bool = json.get("require_colons", False)
        self.managed: bool = json.get("managed", False)
        self.animated: bool = json.get("animated", False)
        self.available: bool = json.get("available", False)

class Reaction:
    def __init__(self, json: Dict) -> None:
        if json == None:
            self = None
            return
        self.count: int = json["count"]
        self.me: bool = json["me"]
        self.emoji: Emoji = Emoji(json["emoji"])

class MessageActivityType(enum.Enum):
    JOIN = 1
    SPECTATE = 2
    LISTEN = 3
    JOIN_REQUEST = 5

class MessageActivity:
    def __init__(self, json: Dict) -> None:
        if json == None:
            self = None
            return
        self.type: MessageActivityType = MessageActivityType(json["type"])
        self.party_id: str = json.get("party_id", None)

class MessageReference:
    def __init__(self, json: Dict) -> None:
        if json == None:
            self = None
            return
        self.message_id: str = json.get("message_id", None)
        self.channel_id: str = json.get("channel_id", None)
        self.guild_id: str = json.get("guild_id", None)
        self.fail_if_not_exists: bool = json.get("fail_if_not_exists", None)
    def to_json(self) -> Dict[str, any]:
        result = {}

        if self.message_id != None and type(self.message_id) == str:
            result["message_id"] = self.message_id
        elif self.channel_id != None and type(self.channel_id) == str:
            result["channel_id"] = self.channel_id
        elif self.guild_id != None and type(self.guild_id) == str:
            result["guild_id"] = self.guild_id
        elif self.fail_if_not_exists != None and type(self.fail_if_not_exists) == bool:
            result["fail_if_not_exists"] = self.fail_if_not_exists

        return result

class MessageInteractionType(enum.Enum):
    PING = 1
    APPLICATION_COMMAND = 2
    MESSAGE_COMPONENT = 3
    APPLICATION_COMMAND_AUTOCOMPLETE = 4
    MODAL_SUBMIT = 5

class MessageInteraction:
    def __init__(self, json: Dict) -> None:
        if json == None:
            self = None
            return
        self.id: str = json["id"]
        self.type: MessageInteractionType = MessageInteractionType(json["type"])
        self.name: str = json["name"]
        self.user: User = User(json["user"])
        self.member: GuildMember = json.get("member", None)
        if not self.member is None:
            self.member = GuildMember(self.member)

class StickerFormatTypes(enum.Enum):
    PNG = 1
    APNG = 2
    LOTTIE = 3

class StickerItem:
    def __init__(self, json: Dict) -> None:
        if json == None:
            self = None
            return
        self.id: str = json["id"]
        self.name: str = json["name"]
        self.format_type: StickerFormatTypes = StickerFormatTypes(json["format_type"])

class StickerTypes(enum.Enum):
    STANDARD = 1
    GUILD = 2

class Sticker:
    def __init__(self, json: Dict) -> None:
        if json == None:
            self = None
            return
        self.id: str = json["id"]
        self.pack_id: str = json.get("pack_id", None)
        self.name: str = json["name"]
        self.description: str = json["description"]
        self.tags: str = json["tags"]
        self.asset: str = json["asset"]
        self.type: StickerTypes = StickerTypes(json["type"])
        self.format_type: StickerFormatTypes = StickerFormatTypes(json["format_type"])
        self.available: bool = json.get("available", None)
        self.guild_id: str = json.get("guild_id", None)
        self.user: User = json.get("user", None)
        if not self.user is None:
            self.user = User(self.user)
        self.sort_value: int = json.get("sort_value", None)

class AllowedMentionTypes(enum.Enum):
    ROLE = "roles"
    USER = "users"
    EVERYONE = "everyone"

class AllowedMentions:
    def __init__(self, parse: List[AllowedMentionTypes], roles: List[str], users: List[str], replied_user: bool):
        self.parse = parse
        self.roles = roles
        self.users = users
        self.replied_user = replied_user
    def to_json(self) -> Dict[str, Any]:
        return {
            "parse": self.parse,
            "roles": self.roles,
            "users": self.users,
            "replied_user": self.replied_user,
        }

class MessageSend:
    def __init__(
        self, 
        content: str = None, 
        tts: bool = None,
        embeds: List[Embed] = None,
        allowed_mentions: AllowedMentions = None,
        message_reference: MessageReference = None,
        sticker_ids: List[str] = None,
        attachments: List[Attachment] = None
    ):
        self.content = content
        self.tts = tts
        self.embeds = embeds
        self.allowed_mentions = allowed_mentions
        self.message_reference = message_reference
        self.sticker_ids = sticker_ids
        self.attachments = attachments
    def to_json(self) -> Dict[str, Any]:
        if self.content == None and self.embeds == None and self.sticker_ids == None:
            raise Exception("MessageSend need one of the content, embeds, and sticker_ids to be set")
        result = {}
        if self.content != None and type(self.content) == str:
            result["content"] = self.content
        if self.tts != None and type(self.tts) == bool:
            result["tts"] = self.tts
        if self.embeds != None and type(self.embeds) == list:
            result["embeds"] = []
            for embed in self.embeds:
                if type(embed) == Embed:
                    result["embeds"].append(embed.to_json())
        if self.allowed_mentions != None and type(self.allowed_mentions) == AllowedMentions:
            result["allowed_mentions"] = self.allowed_mentions.to_json()
        if self.message_reference != None and type(self.message_reference) == MessageReference:
            result["message_reference"] = self.message_reference.to_json()
        if self.sticker_ids != None and type(self.sticker_ids) == list:
            result["sticker_ids"] = []
            for sticker_id in self.sticker_ids:
                if type(sticker_id) == str:
                    result["sticker_ids"].append(sticker_id)
        if self.attachments != None and type(self.attachments) == list:
            result["attachments"] = []
            for attachment in self.attachments:
                if type(attachment) == Attachment:
                    result["attachments"].append(attachment.to_json())
        return result
