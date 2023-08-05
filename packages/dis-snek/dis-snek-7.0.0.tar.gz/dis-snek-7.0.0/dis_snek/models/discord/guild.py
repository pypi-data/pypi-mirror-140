import asyncio
from collections import namedtuple
import logging
import time
from io import IOBase
from pathlib import Path
from typing import List, Optional, Union, Set
from dis_snek.models.snek import AsyncIterator


import attr
from aiohttp import FormData

import dis_snek.models as models
from dis_snek.client.const import MISSING, PREMIUM_GUILD_LIMITS, logger_name, Absent
from dis_snek.client.errors import EventLocationNotProvided
from dis_snek.client.utils.attr_utils import define, docs
from dis_snek.client.utils.converters import optional
from dis_snek.client.utils.converters import timestamp_converter
from dis_snek.client.utils.serializer import to_dict, to_image_data, dict_filter_none, no_export_meta
from .base import DiscordObject, ClientObject
from .enums import (
    NSFWLevels,
    Permissions,
    SystemChannelFlags,
    VerificationLevels,
    DefaultNotificationLevels,
    ExplicitContentFilterLevels,
    MFALevels,
    ChannelTypes,
    IntegrationExpireBehaviour,
    ScheduledEventPrivacyLevel,
    ScheduledEventType,
    AuditLogEventType,
)
from .snowflake import to_snowflake, Snowflake_Type

__all__ = [
    "GuildBan",
    "BaseGuild",
    "GuildWelcome",
    "GuildPreview",
    "Guild",
    "GuildTemplate",
    "GuildWelcomeChannel",
    "GuildIntegration",
    "AuditLogChange",
    "AuditLogEntry",
    "AuditLog",
    "AuditLogHistory",
]

log = logging.getLogger(logger_name)


@define()
class GuildBan:
    reason: Optional[str]
    user: "models.User"


@define()
class BaseGuild(DiscordObject):
    name: str = attr.ib()
    """Name of guild. (2-100 characters, excluding trailing and leading whitespace)"""
    description: Optional[str] = attr.ib(default=None)
    """The description for the guild, if the guild is discoverable"""

    icon: Optional["models.Asset"] = attr.ib(default=None)
    """Icon image asset"""
    splash: Optional["models.Asset"] = attr.ib(default=None)
    """Splash image asset"""
    discovery_splash: Optional["models.Asset"] = attr.ib(default=None)
    """Discovery splash image. Only present for guilds with the "DISCOVERABLE" feature."""
    features: List[str] = attr.ib(factory=list)
    """The features of this guild"""

    @classmethod
    def _process_dict(cls, data, client):
        if icon_hash := data.pop("icon", None):
            data["icon"] = models.Asset.from_path_hash(client, f"icons/{data['id']}/{{}}", icon_hash)
        if splash_hash := data.pop("splash", None):
            data["splash"] = models.Asset.from_path_hash(client, f"splashes/{data['id']}/{{}}", splash_hash)
        if disco_splash := data.pop("discovery_splash", None):
            data["discovery_splash"] = models.Asset.from_path_hash(
                client, f"discovery-splashes/{data['id']}/{{}}", disco_splash
            )
        return data


@define()
class GuildWelcome(ClientObject):
    description: Optional[str] = attr.ib(default=None, metadata=docs("Welcome Screen server description"))
    welcome_channels: List["models.GuildWelcomeChannel"] = attr.ib(
        metadata=docs("List of Welcome Channel objects, up to 5")
    )


@define()
class GuildPreview(BaseGuild):
    emoji: list["models.PartialEmoji"] = attr.ib(factory=list)
    """A list of custom emoji from this guild"""
    approximate_member_count: int = attr.ib(default=0)
    """Approximate number of members in this guild"""
    approximate_presence_count: int = attr.ib(default=0)
    """Approximate number of online members in this guild"""

    @classmethod
    def _process_dict(cls, data, client):
        return super()._process_dict(data, client)


@define()
class Guild(BaseGuild):
    """Guilds in Discord represent an isolated collection of users and channels, and are often referred to as "servers" in the UI."""

    unavailable: bool = attr.ib(default=False)
    """True if this guild is unavailable due to an outage."""
    # owner: bool = attr.ib(default=False)  # we get this from api but it's kinda useless to store
    afk_channel_id: Optional[Snowflake_Type] = attr.ib(default=None)
    """The channel id for afk."""
    afk_timeout: Optional[int] = attr.ib(default=None)
    """afk timeout in seconds."""
    widget_enabled: bool = attr.ib(default=False)
    """True if the server widget is enabled."""
    widget_channel_id: Optional[Snowflake_Type] = attr.ib(default=None)
    """The channel id that the widget will generate an invite to, or None if set to no invite."""
    verification_level: Union[VerificationLevels, int] = attr.ib(default=VerificationLevels.NONE)
    """The verification level required for the guild."""
    default_message_notifications: Union[DefaultNotificationLevels, int] = attr.ib(
        default=DefaultNotificationLevels.ALL_MESSAGES
    )
    """The default message notifications level."""
    explicit_content_filter: Union[ExplicitContentFilterLevels, int] = attr.ib(
        default=ExplicitContentFilterLevels.DISABLED
    )
    """The explicit content filter level."""
    mfa_level: Union[MFALevels, int] = attr.ib(default=MFALevels.NONE)
    """The required MFA (Multi Factor Authentication) level for the guild."""
    system_channel_id: Optional[Snowflake_Type] = attr.ib(default=None)
    """The id of the channel where guild notices such as welcome messages and boost events are posted."""
    system_channel_flags: Union[SystemChannelFlags, int] = attr.ib(default=SystemChannelFlags.NONE)
    """The system channel flags."""
    rules_channel_id: Optional[Snowflake_Type] = attr.ib(default=None)
    """The id of the channel where Community guilds can display rules and/or guidelines."""
    joined_at: str = attr.ib(default=None, converter=optional(timestamp_converter))
    """When this guild was joined at."""
    large: bool = attr.ib(default=False)
    """True if this is considered a large guild."""
    member_count: int = attr.ib(default=0)
    """The total number of members in this guild."""
    voice_states: List[dict] = attr.ib(factory=list)
    """The states of members currently in voice channels. Lacks the guild_id key."""
    presences: List[dict] = attr.ib(factory=list)
    """The presences of the members in the guild, will only include non-offline members if the size is greater than large threshold."""
    max_presences: Optional[int] = attr.ib(default=None)
    """The maximum number of presences for the guild. (None is always returned, apart from the largest of guilds)"""
    max_members: Optional[int] = attr.ib(default=None)
    """The maximum number of members for the guild."""
    vanity_url_code: Optional[str] = attr.ib(default=None)
    """The vanity url code for the guild."""
    banner: Optional[str] = attr.ib(default=None)
    """Hash for banner image."""
    premium_tier: Optional[str] = attr.ib(default=None)
    """The premium tier level. (Server Boost level)"""
    premium_subscription_count: int = attr.ib(default=0)
    """The number of boosts this guild currently has."""
    preferred_locale: str = attr.ib()
    """The preferred locale of a Community guild. Used in server discovery and notices from Discord. Defaults to \"en-US\""""
    public_updates_channel_id: Optional[Snowflake_Type] = attr.ib(default=None)
    """The id of the channel where admins and moderators of Community guilds receive notices from Discord."""
    max_video_channel_users: int = attr.ib(default=0)
    """The maximum amount of users in a video channel."""
    welcome_screen: Optional["GuildWelcome"] = attr.ib(default=None)
    """The welcome screen of a Community guild, shown to new members, returned in an Invite's guild object."""
    nsfw_level: Union[NSFWLevels, int] = attr.ib(default=NSFWLevels.DEFAULT)
    """The guild NSFW level."""
    stage_instances: List[dict] = attr.ib(factory=list)  # TODO stage instance objects
    """Stage instances in the guild."""
    chunked = attr.ib(factory=asyncio.Event, metadata=no_export_meta)
    """An event that is fired when this guild has been chunked"""

    _owner_id: Snowflake_Type = attr.ib(converter=to_snowflake)
    _channel_ids: Set[Snowflake_Type] = attr.ib(factory=set)
    _thread_ids: Set[Snowflake_Type] = attr.ib(factory=set)
    _member_ids: Set[Snowflake_Type] = attr.ib(factory=set)
    _role_ids: Set[Snowflake_Type] = attr.ib(factory=set)
    _chunk_cache: list = attr.ib(factory=list)

    @classmethod
    def _process_dict(cls, data, client):
        # todo: find a away to prevent this loop from blocking the event loop
        data = super()._process_dict(data, client)
        guild_id = data["id"]

        channels_data = data.pop("channels", [])
        for c in channels_data:
            c["guild_id"] = guild_id
        data["channel_ids"] = {client.cache.place_channel_data(channel_data).id for channel_data in channels_data}

        threads_data = data.pop("threads", [])
        data["thread_ids"] = {client.cache.place_channel_data(thread_data).id for thread_data in threads_data}

        members_data = data.pop("members", [])
        data["member_ids"] = {client.cache.place_member_data(guild_id, member_data).id for member_data in members_data}

        roles_data = data.pop("roles", [])
        data["role_ids"] = set(client.cache.place_role_data(guild_id, roles_data).keys())

        if welcome_screen := data.get("welcome_screen"):
            data["welcome_screen"] = GuildWelcome.from_dict(welcome_screen, client)
        return data

    @property
    def channels(self) -> List["models.TYPE_GUILD_CHANNEL"]:
        """Returns a list of channels associated with this guild."""
        return [self._client.cache.channel_cache.get(c_id) for c_id in self._channel_ids]

    @property
    def threads(self) -> List["models.TYPE_THREAD_CHANNEL"]:
        """Returns a list of threads associated with this guild."""
        return [self._client.cache.channel_cache.get(t_id) for t_id in self._thread_ids]

    @property
    def members(self) -> List["models.Member"]:
        """Returns a list of all members within this guild."""
        return [self._client.cache.member_cache.get((self.id, m_id)) for m_id in self._member_ids]

    @property
    def premium_subscribers(self) -> List["models.Member"]:
        """Returns a list of all premium subscribers"""
        return [member for member in self.members if member.premium]

    @property
    def bots(self) -> List["models.Member"]:
        """Returns a list of all bots within this guild"""
        return [member for member in self.members if member.bot]

    @property
    def humans(self) -> List["models.Member"]:
        """Returns a list of all humans within this guild"""
        return [member for member in self.members if not member.bot]

    @property
    def roles(self) -> List["models.Role"]:
        """Returns a list of roles associated with this guild."""
        return [self._client.cache.role_cache.get(r_id) for r_id in self._role_ids]

    @property
    def me(self) -> "models.Member":
        """Returns this bots member object within this guild."""
        return self._client.cache.member_cache.get((self.id, self._client.user.id))

    @property
    def system_channel(self) -> Optional["models.GuildText"]:
        """Returns the channel this guild uses for system messages."""
        return self._client.cache.channel_cache.get(self.system_channel_id)

    @property
    def rules_channel(self) -> Optional["models.GuildText"]:
        """Returns the channel declared as a rules channel."""
        return self._client.cache.channel_cache.get(self.rules_channel_id)

    @property
    def public_updates_channel(self) -> Optional["models.GuildText"]:
        """Returns the channel where server staff receive notices from Discord."""
        return self._client.cache.channel_cache.get(self.public_updates_channel_id)

    @property
    def emoji_limit(self) -> int:
        """The maximum number of emoji this guild can have."""
        base = 200 if "MORE_EMOJI" in self.features else 50
        return max(base, PREMIUM_GUILD_LIMITS[self.premium_tier]["emoji"])

    @property
    def sticker_limit(self) -> int:
        """The maximum number of stickers this guild can have."""
        base = 60 if "MORE_STICKERS" in self.features else 0
        return max(base, PREMIUM_GUILD_LIMITS[self.premium_tier]["stickers"])

    @property
    def bitrate_limit(self) -> int:
        """The maximum bitrate for this guild."""
        base = 128000 if "VIP_REGIONS" in self.features else 96000
        return max(base, PREMIUM_GUILD_LIMITS[self.premium_tier]["bitrate"])

    @property
    def filesize_limit(self) -> int:
        """The maximum filesize that may be uploaded within this guild."""
        return PREMIUM_GUILD_LIMITS[self.premium_tier]["filesize"]

    @property
    def default_role(self) -> "models.Role":
        """The `@everyone` role in this guild."""
        return self._client.cache.role_cache.get(self.id)  # type: ignore

    @property
    def premium_subscriber_role(self) -> Optional["models.Role"]:
        """The role given to boosters of this server, if set."""
        for role in self.roles:
            if role.premium_subscriber:
                return role
        return None

    @property
    def my_role(self) -> Optional["models.Role"]:
        """The role associated with this client, if set."""
        m_r_id = self._client.user.id
        for role in self.roles:
            if role._bot_id == m_r_id:
                return role
        return None

    @property
    def permissions(self) -> Permissions:
        """Alias for me.guild_permissions"""
        return self.me.guild_permissions

    async def fetch_member(self, member_id: Snowflake_Type) -> Optional["models.Member"]:
        """
        Return the Member with the given discord ID, fetching from the API if necessary.

        Args:
            member_id: The ID of the member:
        Returns:
            Member object or None
        """
        return await self._client.cache.fetch_member(self.id, member_id)

    def get_member(self, member_id: Snowflake_Type) -> Optional["models.Member"]:
        """
        Return the Member with the given discord ID.

        Args:
            member_id: The ID of the member:
        Returns:
            Member object or None
        """
        return self._client.cache.get_member(self.id, member_id)

    async def fetch_owner(self) -> "models.Member":
        """
        Return the Guild owner

        Returns:
            Member object or None
        """
        # TODO: maybe precache owner instead of using `fetch_owner`
        return await self._client.cache.fetch_member(self.id, self._owner_id)

    def get_owner(self) -> "models.Member":
        """
        Return the Guild owner

        Returns:
            Member object or None
        """
        return self._client.cache.get_member(self.id, self._owner_id)

    def is_owner(self, user: Snowflake_Type) -> bool:
        """
        Whether the user is owner of the guild.

        Args:
            user: The user to check

        Note:
            the `user` argument can be any type that meets `Snowflake_Type`
        """
        return self._owner_id == to_snowflake(user)

    async def edit_nickname(self, new_nickname: Absent[str] = MISSING, reason: Absent[str] = MISSING) -> None:
        """Alias for me.edit_nickname"""
        await self.me.edit_nickname(new_nickname, reason=reason)

    async def chunk_guild(self, wait=True, presences=False) -> None:
        """
        Trigger a gateway `get_members` event, populating this object with members.

        Args:
            wait: Wait for chunking to be completed before continuing
            presences: Do you need presence data for members?

        """
        await self._client.ws.request_member_chunks(self.id, limit=0, presences=presences)
        if wait:
            await self.chunked.wait()

    async def process_member_chunk(self, chunk: dict) -> None:
        """
        Receive and either cache or process the chunks of members from gateway.

        Args:
            chunk: A member chunk from discord
        """
        if self.chunked.is_set():
            self.chunked.clear()

        if not self._chunk_cache:
            self._chunk_cache: List = chunk.get("members")
        else:
            self._chunk_cache = self._chunk_cache + chunk.get("members")

        if chunk.get("chunk_index") != chunk.get("chunk_count") - 1:
            return log.debug(f"Cached chunk of {len(chunk.get('members'))} members for {self.id}")
        else:
            members = self._chunk_cache
            log.info(f"Processing {len(members)} members for {self.id}")

            s = time.monotonic()
            start_time = time.perf_counter()

            for member in members:
                self._client.cache.place_member_data(self.id, member)
                if (time.monotonic() - s) > 0.05:
                    # look, i get this *could* be a thread, but because it needs to modify data in the main thread,
                    # it is still blocking. So by periodically yielding to the event loop, we can avoid blocking, and still
                    # process this data properly
                    await asyncio.sleep(0)
                    s = time.monotonic()

            total_time = time.perf_counter() - start_time
            self.chunk_cache = []
            log.info(f"Cached members for {self.id} in {total_time:.2f} seconds")
            self.chunked.set()

    async def fetch_audit_log(
        self,
        user_id: Optional["Snowflake_Type"] = MISSING,
        action_type: Optional["AuditLogEventType"] = MISSING,
        before: Optional["Snowflake_Type"] = MISSING,
        after: Optional["Snowflake_Type"] = MISSING,
        limit: int = 100,
    ) -> "AuditLog":
        """
        Fetch section of the audit log for this guild.

        Args:
            user_id: The ID of the user to filter by
            action_type: The type of action to filter by
            before: The ID of the entry to start at
            after: The ID of the entry to end at
            limit: The number of entries to return

        Returns:
            An AuditLog object
        """
        data = await self._client.http.get_audit_log(self.id, user_id, action_type, before, after, limit)
        return AuditLog.from_dict(data, self._client)

    def audit_log_history(
        self,
        user_id: Optional["Snowflake_Type"] = MISSING,
        action_type: Optional["AuditLogEventType"] = MISSING,
        before: Optional["Snowflake_Type"] = MISSING,
        after: Optional["Snowflake_Type"] = MISSING,
        limit: int = 100,
    ) -> "AuditLogHistory":
        """
        Get an async iterator for the history of the audit log.

        Parameters:
            guild (:class:`Guild`): The guild to search through.
            user_id (:class:`Snowflake_Type`): The user ID to search for.
            action_type (:class:`AuditLogEventType`): The action type to search for.
            before: get entries before this message ID
            after: get entries after this message ID
            limit: The maximum number of entries to return (set to 0 for no limit)

        ??? Hint "Example Usage:"
            ```python
            async for entry in guild.audit_log_history(limit=0):
                entry: "AuditLogEntry"
                if entry.changes:
                    # ...
            ```
            or
            ```python
            history = guild.audit_log_history(limit=250)
            # Flatten the async iterator into a list
            entries = await history.flatten()
            ```

        Returns:
            AuditLogHistory (AsyncIterator)

        """
        return AuditLogHistory(self, user_id, action_type, before, after, limit)

    async def edit(
        self,
        name: Absent[Optional[str]] = MISSING,
        description: Absent[Optional[str]] = MISSING,
        verification_level: Absent[Optional["models.VerificationLevels"]] = MISSING,
        default_message_notifications: Absent[Optional["DefaultNotificationLevels"]] = MISSING,
        explicit_content_filter: Absent[Optional["ExplicitContentFilterLevels"]] = MISSING,
        afk_channel: Absent[Optional[Union["models.GuildVoice", Snowflake_Type]]] = MISSING,
        afk_timeout: Absent[Optional[int]] = MISSING,
        system_channel: Absent[Optional[Union["models.GuildText", Snowflake_Type]]] = MISSING,
        system_channel_flags: Absent[Optional[SystemChannelFlags]] = MISSING,
        # ToDo: these are not tested. Mostly, since I do not have access to those features
        owner: Absent[Optional[Union["models.Member", Snowflake_Type]]] = MISSING,
        icon: Absent[Optional[Union[str, "Path", "IOBase"]]] = MISSING,
        splash: Absent[Optional[Union["models.File", "IOBase", "Path", str, bytes]]] = MISSING,
        discovery_splash: Absent[Optional[Union[str, "Path", "IOBase"]]] = MISSING,
        banner: Absent[Optional[Union[str, "Path", "IOBase"]]] = MISSING,
        rules_channel: Absent[Optional[Union["models.GuildText", Snowflake_Type]]] = MISSING,
        public_updates_channel: Absent[Optional[Union["models.GuildText", Snowflake_Type]]] = MISSING,
        preferred_locale: Absent[Optional[str]] = MISSING,
        # ToDo: validate voice region
        region: Absent[Optional[str]] = MISSING,
        # ToDo: Fill in guild features. No idea how this works - https://discord.com/developers/docs/resources/guild#guild-object-guild-features
        features: Absent[Optional[list[str]]] = MISSING,
        reason: Absent[Optional[str]] = MISSING,
    ) -> None:
        """
        Edit the guild.

        Parameters:
            name: The new name of the guild.
            description: The new description of the guild.
            region: ToDo
            verification_level: The new verification level for the guild.
            default_message_notifications: The new notification level for the guild.
            explicit_content_filter: The new explicit content filter level for the guild.
            afk_channel: The voice channel that should be the new AFK channel.
            afk_timeout: How many seconds does a member need to be afk before they get moved to the AFK channel. Must be either `60`, `300`, `900`, `1800` or `3600`, otherwise HTTPException will be raised.
            icon: The new icon. Requires a bytes like object or a path to an image.
            owner: The new owner of the guild. You, the bot, need to be owner for this to work.
            splash: The new invite splash image. Requires a bytes like object or a path to an image.
            discovery_splash: The new discovery image. Requires a bytes like object or a path to an image.
            banner: The new banner image. Requires a bytes like object or a path to an image.
            system_channel: The text channel where new system messages should appear. This includes boosts and welcome messages.
            system_channel_flags: The new settings for the system channel.
            rules_channel: The text channel where your rules and community guidelines are displayed.
            public_updates_channel: The text channel where updates from discord should appear.
            preferred_locale: The new preferred locale of the guild. Must be an ISO 639 code.
            features: ToDo
            reason: An optional reason for the audit log.

        """
        await self._client.http.modify_guild(
            guild_id=self.id,
            name=name,
            description=description,
            region=region,
            verification_level=int(verification_level) if verification_level else MISSING,
            default_message_notifications=int(default_message_notifications)
            if default_message_notifications
            else MISSING,
            explicit_content_filter=int(explicit_content_filter) if explicit_content_filter else MISSING,
            afk_channel_id=to_snowflake(afk_channel) if afk_channel else MISSING,
            afk_timeout=afk_timeout,
            icon=to_image_data(icon) if icon else MISSING,
            owner_id=to_snowflake(owner) if owner else MISSING,
            splash=to_image_data(splash) if splash else MISSING,
            discovery_splash=to_image_data(discovery_splash) if discovery_splash else MISSING,
            banner=to_image_data(banner) if banner else MISSING,
            system_channel_id=to_snowflake(system_channel) if system_channel else MISSING,
            system_channel_flags=int(system_channel_flags) if system_channel_flags else MISSING,
            rules_channel_id=to_snowflake(rules_channel) if rules_channel else MISSING,
            public_updates_channel_id=to_snowflake(public_updates_channel) if public_updates_channel else MISSING,
            preferred_locale=preferred_locale,
            features=features,
            reason=reason,
        )

    async def create_custom_emoji(
        self,
        name: str,
        imagefile: Union["models.File", "IOBase", "Path", str, bytes],
        roles: Optional[List[Union[Snowflake_Type, "models.Role"]]] = None,
        reason: Absent[Optional[str]] = MISSING,
    ) -> "models.CustomEmoji":
        """
        Create a new custom emoji for the guild.

        parameters:
            name: Name of the emoji
            imagefile: The emoji image. (Supports PNG, JPEG, WebP, GIF)
            roles: Roles allowed to use this emoji.
            reason: An optional reason for the audit log.

        returns:
            The new custom emoji created.

        """
        data_payload = dict_filter_none(
            {
                "name": name,
                "image": to_image_data(imagefile),
                "roles": roles,
            }
        )

        emoji_data = await self._client.http.create_guild_emoji(data_payload, self.id, reason=reason)
        emoji_data["guild_id"] = self.id
        return self._client.cache.place_emoji_data(self.id, emoji_data)

    async def create_guild_template(self, name: str, description: str = None) -> "models.GuildTemplate":

        template = await self._client.http.create_guild_template(self.id, name, description)
        return GuildTemplate.from_dict(template, self._client)

    async def fetch_guild_templates(self) -> List["models.GuildTemplate"]:
        templates = await self._client.http.get_guild_templates(self.id)
        return [GuildTemplate.from_dict(t, self._client) for t in templates]

    async def fetch_all_custom_emojis(self) -> List["models.CustomEmoji"]:
        """
        Gets all the custom emoji present for this guild.

        returns:
            A list of custom emoji objects.

        """
        emojis_data = await self._client.http.get_all_guild_emoji(self.id)
        return [self._client.cache.place_emoji_data(self.id, emoji_data) for emoji_data in emojis_data]

    async def fetch_custom_emoji(self, emoji_id: Snowflake_Type) -> "models.CustomEmoji":
        """
        Fetches the custom emoji present for this guild, based on the emoji id.

        parameters:
            emoji_id: The target emoji to get data of.

        returns:
            The custom emoji object.

        """
        return await self._client.cache.fetch_emoji(self.id, emoji_id)

    def get_custom_emoji(self, emoji_id: Snowflake_Type) -> "models.CustomEmoji":
        """
        Gets the custom emoji present for this guild, based on the emoji id.

        parameters:
            emoji_id: The target emoji to get data of.

        returns:
            The custom emoji object.

        """
        emoji_id = to_snowflake(emoji_id)
        emoji = self._client.cache.get_emoji(emoji_id)
        if emoji and emoji._guild_id == self.id:
            return emoji
        return None

    async def create_channel(
        self,
        channel_type: Union[ChannelTypes, int],
        name: str,
        topic: Absent[Optional[str]] = MISSING,
        position: Absent[Optional[int]] = MISSING,
        permission_overwrites: Absent[Optional[List[Union["models.PermissionOverwrite", dict]]]] = MISSING,
        category: Union[Snowflake_Type, "models.GuildCategory"] = None,
        nsfw: bool = False,
        bitrate: int = 64000,
        user_limit: int = 0,
        rate_limit_per_user: int = 0,
        reason: Absent[Optional[str]] = MISSING,
    ) -> "models.TYPE_GUILD_CHANNEL":
        """
        Create a guild channel, allows for explicit channel type setting.

        parameters:
            channel_type: The type of channel to create
            name: The name of the channel
            topic: The topic of the channel
            position: The position of the channel in the channel list
            permission_overwrites: Permission overwrites to apply to the channel
            category: The category this channel should be within
            nsfw: Should this channel be marked nsfw
            bitrate: The bitrate of this channel, only for voice
            user_limit: The max users that can be in this channel, only for voice
            rate_limit_per_user: The time users must wait between sending messages
            reason: The reason for creating this channel

        returns:
            The newly created channel.

        """
        if category:
            category = to_snowflake(category)

        if permission_overwrites:
            permission_overwrites = list(map(to_dict, permission_overwrites))

        channel_data = await self._client.http.create_guild_channel(
            self.id,
            name,
            channel_type,
            topic,
            position,
            permission_overwrites,
            category,
            nsfw,
            bitrate,
            user_limit,
            rate_limit_per_user,
            reason,
        )
        return self._client.cache.place_channel_data(channel_data)

    async def create_text_channel(
        self,
        name: str,
        topic: Absent[Optional[str]] = MISSING,
        position: Absent[Optional[int]] = MISSING,
        permission_overwrites: Absent[Optional[List[Union["models.PermissionOverwrite", dict]]]] = MISSING,
        category: Union[Snowflake_Type, "models.GuildCategory"] = None,
        nsfw: bool = False,
        rate_limit_per_user: int = 0,
        reason: Absent[Optional[str]] = MISSING,
    ) -> "models.GuildText":
        """
        Create a text channel in this guild.

        parameters:
            name: The name of the channel
            topic: The topic of the channel
            position: The position of the channel in the channel list
            permission_overwrites: Permission overwrites to apply to the channel
            category: The category this channel should be within
            nsfw: Should this channel be marked nsfw
            rate_limit_per_user: The time users must wait between sending messages
            reason: The reason for creating this channel

        returns:
           The newly created text channel.

        """
        return await self.create_channel(
            channel_type=ChannelTypes.GUILD_TEXT,
            name=name,
            topic=topic,
            position=position,
            permission_overwrites=permission_overwrites,
            category=category,
            nsfw=nsfw,
            rate_limit_per_user=rate_limit_per_user,
            reason=reason,
        )

    async def create_voice_channel(
        self,
        name: str,
        topic: Absent[Optional[str]] = MISSING,
        position: Absent[Optional[int]] = MISSING,
        permission_overwrites: Absent[Optional[List[Union["models.PermissionOverwrite", dict]]]] = MISSING,
        category: Union[Snowflake_Type, "models.GuildCategory"] = None,
        nsfw: bool = False,
        bitrate: int = 64000,
        user_limit: int = 0,
        reason: Absent[Optional[str]] = MISSING,
    ) -> "models.GuildVoice":
        """
        Create a guild voice channel.

        parameters:
            name: The name of the channel
            topic: The topic of the channel
            position: The position of the channel in the channel list
            permission_overwrites: Permission overwrites to apply to the channel
            category: The category this channel should be within
            nsfw: Should this channel be marked nsfw
            bitrate: The bitrate of this channel, only for voice
            user_limit: The max users that can be in this channel, only for voice
            reason: The reason for creating this channel

        returns:
           The newly created voice channel.

        """
        return await self.create_channel(
            channel_type=ChannelTypes.GUILD_VOICE,
            name=name,
            topic=topic,
            position=position,
            permission_overwrites=permission_overwrites,
            category=category,
            nsfw=nsfw,
            bitrate=bitrate,
            user_limit=user_limit,
            reason=reason,
        )

    async def create_stage_channel(
        self,
        name: str,
        topic: Absent[Optional[str]] = MISSING,
        position: Absent[Optional[int]] = MISSING,
        permission_overwrites: Absent[Optional[List[Union["models.PermissionOverwrite", dict]]]] = MISSING,
        category: Absent[Union[Snowflake_Type, "models.GuildCategory"]] = MISSING,
        bitrate: int = 64000,
        user_limit: int = 0,
        reason: Absent[Optional[str]] = MISSING,
    ) -> "models.GuildStageVoice":
        """
        Create a guild stage channel.

        parameters:
            name: The name of the channel
            topic: The topic of the channel
            position: The position of the channel in the channel list
            permission_overwrites: Permission overwrites to apply to the channel
            category: The category this channel should be within
            bitrate: The bitrate of this channel, only for voice
            user_limit: The max users that can be in this channel, only for voice
            reason: The reason for creating this channel

        returns:
            The newly created stage channel.

        """
        return await self.create_channel(
            channel_type=ChannelTypes.GUILD_STAGE_VOICE,
            name=name,
            topic=topic,
            position=position,
            permission_overwrites=permission_overwrites,
            category=category,
            bitrate=bitrate,
            user_limit=user_limit,
            reason=reason,
        )

    async def create_category(
        self,
        name: str,
        position: Absent[Optional[int]] = MISSING,
        permission_overwrites: Absent[Optional[List[Union["models.PermissionOverwrite", dict]]]] = MISSING,
        reason: Absent[Optional[str]] = MISSING,
    ) -> "models.GuildCategory":
        """
        Create a category within this guild.

        parameters:
            name: The name of the channel
            position: The position of the channel in the channel list
            permission_overwrites: Permission overwrites to apply to the channel
            reason: The reason for creating this channel

        returns:
            The newly created category.

        """
        return await self.create_channel(
            channel_type=ChannelTypes.GUILD_CATEGORY,
            name=name,
            position=position,
            permission_overwrites=permission_overwrites,
            reason=reason,
        )

    async def delete_channel(
        self, channel: Union["models.TYPE_GUILD_CHANNEL", Snowflake_Type], reason: str = None
    ) -> None:
        """
        Delete the given channel, can handle either a snowflake or channel object.

        This is effectively just an alias for `channel.delete()`

        Args:
            channel: The channel to be deleted
            reason: The reason for this deletion

        """
        if isinstance(channel, (str, int)):
            channel = await self._client.get_channel(channel)

        if not channel:
            raise ValueError("Unable to find requested channel")

        # TODO self._channel_ids is not updated properly when new guild channels are created so this check is
        #  disabled for now
        # if channel.id not in self._channel_ids:
        #     raise ValueError("This guild does not hold the requested channel")

        await channel.delete(reason)

    async def list_scheduled_events(self, with_user_count: bool = False) -> List["models.ScheduledEvent"]:
        """
        List all scheduled events in this guild.

        returns:
            A list of scheduled events.

        """
        scheduled_events_data = await self._client.http.list_schedules_events(self.id, with_user_count)
        return models.ScheduledEvent.from_list(scheduled_events_data, self._client)

    async def fetch_scheduled_event(
        self, scheduled_event_id: Snowflake_Type, with_user_count: bool = False
    ) -> "models.ScheduledEvent":
        """
        Get a scheduled event by id.

        Args:
            event_id: The id of the scheduled event.

        returns:
            The scheduled event.

        """
        scheduled_event_data = await self._client.http.get_scheduled_event(self.id, scheduled_event_id, with_user_count)
        return models.ScheduledEvent.from_dict(scheduled_event_data, self._client)

    async def create_scheduled_event(
        self,
        name: str,
        event_type: ScheduledEventType,
        start_time: "models.Timestamp",
        end_time: Absent[Optional["models.Timestamp"]] = MISSING,
        description: Absent[Optional[str]] = MISSING,
        channel_id: Absent[Optional[Snowflake_Type]] = MISSING,
        external_location: Absent[Optional[str]] = MISSING,
        entity_metadata: Optional[dict] = None,
        privacy_level: ScheduledEventPrivacyLevel = ScheduledEventPrivacyLevel.GUILD_ONLY,
        reason: Absent[Optional[str]] = MISSING,
    ) -> "models.ScheduledEvent":
        """
        Create a scheduled guild event.

        Args:
            name: event name
            event_type: event type
            start_time: `Timestamp` object
            end_time: `Timestamp` object
            description: event description
            channel_id: channel id
            external_location: event external location (For external events)
            entity_metadata: event metadata (additional data for the event)
            privacy_level: event privacy level
            reason: reason for creating this scheduled event

        Returns:
            ScheduledEvent object

        !!! note
            For external events, external_location is required
            For voice/stage events, channel_id is required

        ??? note
            entity_metadata is the backend dictionary for fluff fields. Where possible, we plan to expose these fields directly.
            The full list of supported fields is https://discord.com/developers/docs/resources/guild-scheduled-event#guild-scheduled-event-object-guild-scheduled-event-entity-metadata
            Example: `entity_metadata=dict(location="cool place")`

        """
        if external_location is not MISSING:
            entity_metadata = {"location": external_location}

        if event_type == ScheduledEventType.EXTERNAL:
            if external_location == MISSING:
                raise EventLocationNotProvided("Location is required for external events")

        payload = {
            "name": name,
            "entity_type": event_type,
            "scheduled_start_time": start_time.isoformat(),
            "scheduled_end_time": end_time.isoformat() if end_time is not MISSING else end_time,
            "description": description,
            "channel_id": channel_id,
            "entity_metadata": entity_metadata,
            "privacy_level": privacy_level,
        }

        scheduled_event_data = await self._client.http.create_scheduled_event(self.id, payload, reason)
        return models.ScheduledEvent.from_dict(scheduled_event_data, self._client)

    async def create_custom_sticker(
        self,
        name: str,
        imagefile: Union[str, "Path", "IOBase"],
        description: Absent[Optional[str]] = MISSING,
        tags: Absent[Optional[str]] = MISSING,
        reason: Absent[Optional[str]] = MISSING,
    ) -> "models.Sticker":
        """
        Creates a custom sticker for a guild.

        Args:
            name: Sticker name
            imagefile: Sticker image file
            description: Sticker description
            tags: Sticker tags
            reason: Reason for creating the sticker

        Returns:
            New Sticker instance

        """
        payload = FormData()
        payload.add_field("name", name)

        # TODO Validate image type?
        if isinstance(imagefile, IOBase):
            payload.add_field("file", name)
        else:
            payload.add_field("file", open(str(imagefile)))

        if description:
            payload.add_field("description", description)

        if tags:
            payload.add_field("tags", tags)

        sticker_data = await self._client.http.create_guild_sticker(payload, self.id, reason)
        return models.Sticker.from_dict(sticker_data, self._client)

    async def fetch_all_custom_stickers(self) -> List["models.Sticker"]:
        """
        Fetches all custom stickers for a guild.

        Returns:
            List of Sticker objects

        """
        stickers_data = await self._client.http.list_guild_stickers(self.id)
        return models.Sticker.from_list(stickers_data, self._client)

    async def fetch_custom_sticker(self, sticker_id: Snowflake_Type) -> "models.Sticker":
        """
        Fetches a specific custom sticker for a guild.

        Args:
            sticker_id: ID of sticker to get

        Returns:
            Requested Sticker

        """
        sticker_data = await self._client.http.get_guild_sticker(self.id, to_snowflake(sticker_id))
        return models.Sticker.from_dict(sticker_data, self._client)

    async def fetch_active_threads(self) -> "models.ThreadList":
        """
        Fetches all active threads in the guild, including public and private threads. Threads are ordered by their id, in descending order.

        returns:
            List of active threads and thread member object for each returned thread the bot user has joined.

        """
        threads_data = await self._client.http.list_active_threads(self.id)
        return models.ThreadList.from_dict(threads_data, self._client)

    async def fetch_role(self, role_id: Snowflake_Type) -> Optional["models.Role"]:
        """
        Fetch the specified role by ID.

        Args:
            role_id: The ID of the role to get

        Returns:
            A role object or None if the role is not found.

        """
        return await self._client.cache.fetch_role(self.id, role_id)

    def get_role(self, role_id: Snowflake_Type) -> Optional["models.Role"]:
        """
        Get the specified role by ID.

        Args:
            role_id: The ID of the role to get

        Returns:
            A role object or None if the role is not found.

        """
        role_id = to_snowflake(role_id)
        if role_id in self._role_ids:
            return self._client.cache.get_role(role_id)
        return None

    async def create_role(
        self,
        name: Absent[Optional[str]] = MISSING,
        permissions: Absent[Optional[Permissions]] = MISSING,
        colour: Absent[Optional[Union["models.Color", int]]] = MISSING,
        color: Absent[Optional[Union["models.Color", int]]] = MISSING,
        hoist: Optional[bool] = False,
        mentionable: Optional[bool] = False,
        # ToDo: icon needs testing. I have to access to that
        icon: Absent[Optional[Union[str, "Path", "IOBase"]]] = MISSING,
        reason: Absent[Optional[str]] = MISSING,
    ) -> "models.Role":
        """
        Create a new role for the guild. You must have the `manage roles` permission.

        Args:
            name: The name the role should have. `Default: new role`
            permissions: The permissions the role should have. `Default: @everyone permissions`
            colour: The colour of the role. Can be either `Color` or an RGB integer. `Default: BrandColors.BLACK`
            color: Alias for `colour`
            icon: Can be either a bytes like object or a path to an image, or a unicode emoji which is supported by discord.
            hoist: Whether the role is shown separately in the members list. `Default: False`
            mentionable: Whether the role can be mentioned. `Default: False`
            reason: An optional reason for the audit log.

        Returns:
            A role object or None if the role is not found.

        """
        payload = {}

        if name:
            payload.update({"name": name})

        if permissions:
            payload.update({"permissions": str(int(permissions))})

        colour = colour or color
        if colour:
            payload.update({"color": colour.value})

        if hoist:
            payload.update({"hoist": True})

        if mentionable:
            payload.update({"mentionable": True})

        if icon:
            # test if the icon is probably a unicode emoji (str and len() == 1) or a path / bytes obj
            if isinstance(icon, str) and len(icon) == 1:
                payload.update({"unicode_emoji": icon})

            else:
                payload.update({"icon": to_image_data(icon)})

        result = await self._client.http.create_guild_role(guild_id=self.id, payload=payload, reason=reason)
        return self._client.cache.place_role_data(guild_id=self.id, data=[result])[to_snowflake(result["id"])]

    def get_channel(self, channel_id: Snowflake_Type) -> Optional["models.TYPE_GUILD_CHANNEL"]:
        """
        Returns a channel with the given `channel_id`.

        Args:
            channel_id: The ID of the channel to get

        Returns:
            Channel object if found, otherwise None

        """
        channel_id = to_snowflake(channel_id)
        if channel_id in self._channel_ids:
            # theoretically, this could get any channel the client can see,
            # but to make it less confusing to new programmers,
            # i intentionally check that the guild contains the channel first
            return self._client.cache.get_channel(channel_id)
        return None

    async def fetch_channel(self, channel_id: Snowflake_Type) -> Optional["models.TYPE_GUILD_CHANNEL"]:
        """
        Returns a channel with the given `channel_id` from the API.

        Args:
            channel_id: The ID of the channel to get

        Returns:
            Channel object if found, otherwise None

        """
        channel_id = to_snowflake(channel_id)
        if channel_id in self._channel_ids:
            # theoretically, this could get any channel the client can see,
            # but to make it less confusing to new programmers,
            # i intentionally check that the guild contains the channel first
            return await self._client.fetch_channel(channel_id)
        return None

    def get_thread(self, thread_id: Snowflake_Type) -> Optional["models.TYPE_THREAD_CHANNEL"]:
        """
        Returns a Thread with the given `thread_id`.

        Args:
            thread_id: The ID of the thread to get

        Returns:
            Thread object if found, otherwise None

        """
        thread_id = to_snowflake(thread_id)
        if thread_id in self._thread_ids:
            return self._client.cache.channel_cache.get(thread_id)
        return None

    async def fetch_thread(self, thread_id: Snowflake_Type) -> Optional["models.TYPE_THREAD_CHANNEL"]:
        """
        Returns a Thread with the given `thread_id` from the API.

        Args:
            thread_id: The ID of the thread to get

        Returns:
            Thread object if found, otherwise None

        """
        thread_id = to_snowflake(thread_id)
        if thread_id in self._thread_ids:
            return await self._client.get_channel(thread_id)
        return None

    async def prune_members(
        self,
        days: int = 7,
        roles: Optional[List[Snowflake_Type]] = None,
        compute_prune_count: bool = True,
        reason: Absent[str] = MISSING,
    ) -> Optional[int]:
        """
        Begin a guild prune. Removes members from the guild who who have not interacted for the last `days` days. By default, members with roles are excluded from pruning, to include them, pass their role (or role id) in `roles` Requires `kick members` permission.

        Args:
            days: number of days to prune (1-30)
            roles: list of roles to include in the prune
            compute_prune_count: Whether the number of members pruned should be calculated (disable this for large guilds)
            reason: The reason for this prune

        Returns:
            The total number of members pruned, if `compute_prune_count` is set to True, otherwise None

        """
        if roles:
            roles = [str(to_snowflake(r)) for r in roles]

        resp = await self._client.http.begin_guild_prune(
            self.id, days, include_roles=roles, compute_prune_count=compute_prune_count, reason=reason
        )
        return resp["pruned"]

    async def estimate_prune_members(
        self, days: int = 7, roles: List[Union[Snowflake_Type, "models.Role"]] = MISSING
    ) -> int:
        """
        Calculate how many members would be pruned, should `guild.prune_members` be used. By default, members with roles are excluded from pruning, to include them, pass their role (or role id) in `roles`.

        Args:
            days: number of days to prune (1-30)
            roles: list of roles to include in the prune

        Returns:
            Total number of members that would be pruned

        """
        if roles is not MISSING:
            roles = [r.id if isinstance(r, models.Role) else r for r in roles]
        else:
            roles = []

        resp = await self._client.http.get_guild_prune_count(self.id, days=days, include_roles=roles)
        return resp["pruned"]

    async def leave(self) -> None:
        """Leave this guild."""
        await self._client.http.leave_guild(self.id)

    async def delete(self) -> None:
        """
        Delete the guild.

        You must own this guild to do this.

        """
        await self._client.http.delete_guild(self.id)

    async def kick(
        self, user: Union["models.User", "models.Member", Snowflake_Type], reason: Absent[str] = MISSING
    ) -> None:
        """
        Kick a user from the guild.

        You must have the `kick members` permission
        Args:
            user: The user to kick
            reason: The reason for the kick

        """
        await self._client.http.remove_guild_member(self.id, to_snowflake(user), reason=reason)

    async def ban(
        self,
        user: Union["models.User", "models.Member", Snowflake_Type],
        delete_message_days: int = 0,
        reason: Absent[str] = MISSING,
    ) -> None:
        """
        Ban a user from the guild.

        You must have the `ban members` permission
        Args:
            user: The user to ban
            delete_message_days: How many days worth of messages to remove
            reason: The reason for the ban

        """
        await self._client.http.create_guild_ban(self.id, to_snowflake(user), delete_message_days, reason=reason)

    async def fetch_ban(self, user: Union["models.User", "models.Member", Snowflake_Type]) -> GuildBan:
        """
        Fetches the ban information for the specified user in the guild. You must have the `ban members` permission.

        Args:
            user: The user to look up.

        Raises:
            NotFound: If the user is not banned in the guild.

        Returns:
            The ban information.

        """
        ban_info = await self._client.http.get_guild_ban(self.id, to_snowflake(user))
        return GuildBan(reason=ban_info["reason"], user=self._client.cache.place_user_data(ban_info["user"]))

    async def fetch_bans(self) -> list[GuildBan]:
        """
        Fetches all bans for the guild. You must have the `ban members` permission.

        Returns:
            A list containing all bans and information about them.

        """
        ban_infos = await self._client.http.get_guild_bans(self.id)
        return [
            GuildBan(reason=ban_info["reason"], user=self._client.cache.place_user_data(ban_info["user"]))
            for ban_info in ban_infos
        ]

    async def unban(
        self, user: Union["models.User", "models.Member", Snowflake_Type], reason: Absent[str] = MISSING
    ) -> None:
        """
        Unban a user from the guild.

        You must have the `ban members` permission
        Args:
            user: The user to unban
            reason: The reason for the ban

        """
        await self._client.http.remove_guild_ban(self.id, to_snowflake(user), reason=reason)

    async def fetch_widget_image(self, style: str = None) -> str:
        """
        Fetch a guilds widget image.

        For a list of styles, look here: https://discord.com/developers/docs/resources/guild#get-guild-widget-image-widget-style-options

        Args:
            style: The style to use for the widget image

        """
        return await self._client.http.get_guild_widget_image(self.id, style)

    async def fetch_widget(self) -> dict:
        """Fetches the guilds widget."""
        # todo: Guild widget object
        return await self._client.http.get_guild_widget(self.id)

    async def modify_widget(
        self, enabled: bool = None, channel: Union["models.TYPE_GUILD_CHANNEL", Snowflake_Type] = None
    ) -> dict:
        """
        Modify the guild's widget.

        Args:
            enabled: Should the widget be enabled?
            channel: The channel to use in the widget

        """
        if channel:
            if isinstance(channel, DiscordObject):
                channel = channel.id
        return await self._client.http.modify_guild_widget(self.id, enabled, channel)

    async def fetch_invites(self) -> List["models.Invite"]:
        invites_data = await self._client.http.get_guild_invites(self.id)
        return models.Invite.from_list(invites_data, self._client)

    async def fetch_guild_integrations(self) -> List["models.GuildIntegration"]:
        data = await self._client.http.get_guild_integrations(self.id)
        return [GuildIntegration.from_dict(d | {"guild_id": self.id}, self._client) for d in data]

    async def search_members(self, query: str, limit: int = 1) -> List["models.Member"]:
        data = await self._client.http.search_guild_members(guild_id=self.id, query=query, limit=limit)
        return [self._client.cache.place_member_data(self.id, _d) for _d in data]


@define()
class GuildTemplate(ClientObject):
    code: str = attr.ib(metadata=docs("the template code (unique ID)"))
    name: str = attr.ib(metadata=docs("the name"))
    description: Optional[str] = attr.ib(default=None, metadata=docs("the description"))

    usage_count: int = attr.ib(default=0, metadata=docs("number of times this template has been used"))

    creator_id: Snowflake_Type = attr.ib(metadata=docs("The ID of the user who created this template"))
    creator: Optional["models.User"] = attr.ib(default=None, metadata=docs("the user who created this template"))

    created_at: "models.Timestamp" = attr.ib(metadata=docs("When this template was created"))
    updated_at: "models.Timestamp" = attr.ib(metadata=docs("When this template was last synced to the source guild"))

    source_guild_id: Snowflake_Type = attr.ib(metadata=docs("The ID of the guild this template is based on"))
    guild_snapshot: "models.Guild" = attr.ib(metadata=docs("A snapshot of the guild this template contains"))

    is_dirty: bool = attr.ib(default=False, metadata=docs("Whether this template has un-synced changes"))

    @classmethod
    def _process_dict(cls, data, client):
        data["creator"] = client.cache.place_user_data(data["creator"])

        # todo: partial guild obj that **isn't** cached
        data["guild_snapshot"] = data.pop("serialized_source_guild")
        return data

    async def synchronise(self) -> "models.GuildTemplate":
        """Synchronise the template to the source guild's current state."""
        data = await self._client.http.sync_guild_template(self.source_guild_id, self.code)
        self.update_from_dict(data)
        return self

    async def modify(self, name: Optional[str] = None, description: Optional[str] = None) -> "models.GuildTemplate":
        """
        Modify the template's metadata.

        Arguments:
            name: The name for the template
            description: The description for the template

        """
        data = await self._client.http.modify_guild_template(
            self.source_guild_id, self.code, name=name, description=description
        )
        self.update_from_dict(data)
        return self

    async def delete(self) -> None:
        """Delete the guild template."""
        await self._client.http.delete_guild_template(self.source_guild_id, self.code)


@define()
class GuildWelcomeChannel(ClientObject):
    channel_id: Snowflake_Type = attr.ib(metadata=docs("Welcome Channel ID"))
    description: str = attr.ib(metadata=docs("Welcome Channel description"))
    emoji_id: Optional[Snowflake_Type] = attr.ib(
        default=None, metadata=docs("Welcome Channel emoji ID if the emoji is custom")
    )
    emoji_name: Optional[str] = attr.ib(
        default=None, metadata=docs("Emoji name if custom, unicode character if standard")
    )


class GuildIntegration(DiscordObject):
    name: str = attr.ib()
    type: str = attr.ib()
    enabled: bool = attr.ib()
    account: dict = attr.ib()
    application: Optional["models.Application"] = attr.ib(default=None)
    _guild_id: Snowflake_Type = attr.ib()

    syncing: Optional[bool] = attr.ib(default=MISSING)
    role_id: Optional[Snowflake_Type] = attr.ib(default=MISSING)
    enable_emoticons: bool = attr.ib(default=MISSING)
    expire_behavior: IntegrationExpireBehaviour = attr.ib(
        default=MISSING, converter=optional(IntegrationExpireBehaviour)
    )
    expire_grace_period: int = attr.ib(default=MISSING)
    user: "models.BaseUser" = attr.ib(default=MISSING)
    synced_at: "models.Timestamp" = attr.ib(default=MISSING, converter=optional(timestamp_converter))
    subscriber_count: int = attr.ib(default=MISSING)
    revoked: bool = attr.ib(default=MISSING)

    @classmethod
    def from_dict(cls, data, client) -> "GuildIntegration":
        if app := data.get("application", None):
            data["application"] = models.Application.from_dict(app, client)
        if user := data.get("user", None):
            data["user"] = client.cache.place_user_data(user)
        return super().from_dict(data, client)

    async def delete(self, reason: Absent[str] = MISSING) -> None:
        """Delete this guild integration."""
        await self._client.http.delete_guild_integration(self._guild_id, self.id, reason)


@define()
class AuditLogChange(ClientObject):
    key: str = attr.ib()
    new_value: Optional[Union[list, str, int, bool, "Snowflake_Type"]] = attr.ib(default=MISSING)
    old_value: Optional[Union[list, str, int, bool, "Snowflake_Type"]] = attr.ib(default=MISSING)


@define()
class AuditLogEntry(ClientObject):

    id: "Snowflake_Type" = attr.ib(converter=to_snowflake)
    target_id: Optional["Snowflake_Type"] = attr.ib(converter=optional(to_snowflake))
    user_id: "Snowflake_Type" = attr.ib(converter=to_snowflake)
    action_type: "AuditLogEventType" = attr.ib(converter=to_snowflake)
    changes: Optional[List[AuditLogChange]] = attr.ib(default=MISSING)
    options: Optional[Union["Snowflake_Type", str]] = attr.ib(default=MISSING)
    reason: Optional[str] = attr.ib(default=MISSING)

    @classmethod
    def from_dict(cls, data, client) -> "AuditLogEntry":
        if changes := data.get("changes", None):
            data["changes"] = AuditLogChange.from_list(changes, client)
        return super().from_dict(data, client)


@define()
class AuditLog(ClientObject):
    """Contains entries and other data given from selected"""

    entries: Optional[List["AuditLogEntry"]] = attr.ib(default=MISSING)
    scheduled_events: Optional[List["models.ScheduledEvent"]] = attr.ib(default=MISSING)
    integrations: Optional[List["GuildIntegration"]] = attr.ib(default=MISSING)
    threads: Optional[List["models.ThreadChannel"]] = attr.ib(default=MISSING)
    users: Optional[List["models.User"]] = attr.ib(default=MISSING)
    webhooks: Optional[List["models.Webhook"]] = attr.ib(default=MISSING)

    @classmethod
    def from_dict(cls, data, client) -> "AuditLog":
        if entries := data.get("audit_log_entries", None):
            data["entries"] = AuditLogEntry.from_list(entries, client)
        if scheduled_events := data.get("guild_scheduled_events", None):
            data["scheduled_events"] = models.ScheduledEvent.from_list(scheduled_events, client)
        if integrations := data.get("integrations", None):
            data["integrations"] = GuildIntegration.from_list(integrations, client)
        if threads := data.get("threads", None):
            data["threads"] = models.ThreadChannel.from_list(threads, client)
        if users := data.get("users", None):
            data["users"] = models.User.from_list(users, client)
        if webhooks := data.get("webhooks", None):
            data["webhooks"] = models.Webhook.from_list(webhooks, client)
        return super().from_dict(data, client)


class AuditLogHistory(AsyncIterator):
    """
    An async iterator for searching through a audit log's entry history.

    Args:
        guild (:class:`Guild`): The guild to search through.
        user_id (:class:`Snowflake_Type`): The user ID to search for.
        action_type (:class:`AuditLogEventType`): The action type to search for.
        before: get messages before this message ID
        after: get messages after this message ID
        limit: The maximum number of entries to return (set to 0 for no limit)

    """

    def __init__(self, guild, user_id=None, action_type=None, before=None, after=None, limit=50):
        self.guild: "Guild" = guild
        self.user_id: Snowflake_Type = user_id
        self.action_type: "AuditLogEventType" = action_type
        self.before: Snowflake_Type = before
        self.after: Snowflake_Type = after
        super().__init__(limit)

    async def fetch(self) -> List["AuditLog"]:
        if self.after:
            if not self.last:
                self.last = namedtuple("temp", "id")
                self.last.id = self.after
            log = await self.guild.get_audit_log(limit=self.get_limit, after=self.last.id)
            entries = log.entries if log.entries else []

        else:
            if self.before and not self.last:
                self.last = namedtuple("temp", "id")
                self.last.id = self.before

            log = await self.guild.get_audit_log(limit=self.get_limit, before=self.last.id)
            entries = log.entries if log.entries else []
        return entries
