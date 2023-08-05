import copy
from typing import TYPE_CHECKING, Optional, Dict, Any

from dis_snek.client.const import MISSING
from dis_snek.client.utils.attr_utils import define, field
from dis_snek.client.utils.converters import optional as optional_c
from dis_snek.client.utils.converters import timestamp_converter
from dis_snek.models.discord.snowflake import to_snowflake
from dis_snek.models.discord.timestamp import Timestamp
from .base import ClientObject

if TYPE_CHECKING:
    from dis_snek.client import Snake
    from dis_snek.models import Guild, TYPE_VOICE_CHANNEL
    from dis_snek.models.discord.user import Member
    from dis_snek.models.discord.snowflake import Snowflake_Type

__all__ = ["VoiceState"]


@define()
class VoiceState(ClientObject):
    user_id: "Snowflake_Type" = field(default=MISSING, converter=to_snowflake)
    session_id: str = field(default=MISSING)
    deaf: bool = field(default=False)
    mute: bool = field(default=False)
    self_deaf: bool = field(default=False)
    self_mute: bool = field(default=False)
    self_stream: Optional[bool] = field(default=False)
    self_video: bool = field(default=False)
    suppress: bool = field(default=False)
    request_to_speak_timestamp: Optional[Timestamp] = field(default=None, converter=optional_c(timestamp_converter))

    # internal for props
    _guild_id: Optional["Snowflake_Type"] = field(default=None, converter=to_snowflake)
    _channel_id: "Snowflake_Type" = field(converter=to_snowflake)
    _member_id: Optional["Snowflake_Type"] = field(default=None, converter=to_snowflake)

    @property
    def guild(self) -> "Guild":
        """The guild this voice state is for."""
        return self._client.cache.guild_cache.get(self._guild_id) if self._guild_id else None

    @property
    def channel(self) -> "TYPE_VOICE_CHANNEL":
        """The channel the user is connected to."""
        channel = self._client.cache.channel_cache.get(self._channel_id)

        # make sure the member is showing up as a part of the channel
        # this is relevant for VoiceStateUpdate.before
        if self._member_id not in channel._voice_member_ids:
            # create a copy and add the member to that list
            channel = copy.copy(channel)
            channel._voice_member_ids.append(self._member_id)

        return channel

    @property
    def member(self) -> "Member":
        """The member this voice state is for."""
        return self._client.cache.member_cache.get((self._guild_id, self._member_id)) if self._guild_id else None

    @classmethod
    def _process_dict(cls, data: Dict[str, Any], client: "Snake") -> Dict[str, Any]:
        if member := data.pop("member", None):
            member = client.cache.place_member_data(data["guild_id"], member)
            data["member_id"] = member.id

        return data
