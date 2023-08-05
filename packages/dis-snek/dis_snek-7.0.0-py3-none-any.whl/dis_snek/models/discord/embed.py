from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import attr
from attr import setters
from attr.validators import instance_of
from attr.validators import optional as v_optional

from dis_snek.client.const import (
    EMBED_MAX_NAME_LENGTH,
    EMBED_MAX_FIELDS,
    EMBED_MAX_DESC_LENGTH,
    EMBED_TOTAL_MAX,
    EMBED_FIELD_VALUE_LENGTH,
)
from dis_snek.client.mixins.serialization import DictSerializationMixin
from dis_snek.client.utils.attr_utils import field
from dis_snek.client.utils.converters import list_converter, timestamp_converter
from dis_snek.client.utils.converters import optional as c_optional
from dis_snek.client.utils.serializer import no_export_meta, export_converter
from dis_snek.models.discord.color import Color, process_color
from dis_snek.models.discord.timestamp import Timestamp

__all__ = [
    "EmbedField",
    "EmbedAuthor",
    "EmbedAttachment",
    "EmbedAuthor",
    "EmbedFooter",
    "EmbedProvider",
    "Embed",
    "process_embeds",
]


@attr.s(slots=True)
class EmbedField(DictSerializationMixin):
    """
    Representation of an embed field.

    Attributes:
        name: Field name
        value: Field value
        inline: If the field should be inline

    """

    name: str = attr.ib()
    value: str = attr.ib()
    inline: bool = attr.ib(default=False)

    @name.validator
    def _name_validation(self, attribute: str, value: Any) -> None:
        if len(value) > EMBED_MAX_NAME_LENGTH:
            raise ValueError(f"Field name cannot exceed {EMBED_MAX_NAME_LENGTH} characters")

    @value.validator
    def _value_validation(self, attribute: str, value: Any) -> None:
        if len(value) > EMBED_FIELD_VALUE_LENGTH:
            raise ValueError(f"Field value cannot exceed {EMBED_FIELD_VALUE_LENGTH} characters")

    def __len__(self):
        return len(self.name) + len(self.value)


@attr.s(slots=True)
class EmbedAuthor(DictSerializationMixin):
    """
    Representation of an embed author.

    Attributes:
        name: Name to show on embed
        url: Url to go to when name is clicked
        icon_url: Icon to show next to name
        proxy_icon_url: Proxy icon url

    """

    name: Optional[str] = attr.ib(default=None)
    url: Optional[str] = attr.ib(default=None)
    icon_url: Optional[str] = attr.ib(default=None)
    proxy_icon_url: Optional[str] = attr.ib(default=None, metadata=no_export_meta)

    @name.validator
    def _name_validation(self, attribute: str, value: Any) -> None:
        if len(value) > EMBED_MAX_NAME_LENGTH:
            raise ValueError(f"Field name cannot exceed {EMBED_MAX_NAME_LENGTH} characters")

    def __len__(self):
        return len(self.name)


@attr.s(slots=True)
class EmbedAttachment(DictSerializationMixin):  # thumbnail or image or video
    """
    Representation of an attachment.

    Attributes:
        url: Attachment url
        proxy_url: Proxy url
        height: Attachment height
        width: Attachment width

    """

    url: Optional[str] = attr.ib(default=None)
    proxy_url: Optional[str] = attr.ib(default=None, metadata=no_export_meta)
    height: Optional[int] = attr.ib(default=None, metadata=no_export_meta)
    width: Optional[int] = attr.ib(default=None, metadata=no_export_meta)

    @classmethod
    def _process_dict(cls, data: Dict[str, Any]):
        if isinstance(data, str):
            return {"url": data}
        return data

    @property
    def size(self) -> tuple[Optional[int], Optional[int]]:
        return self.height, self.width


@attr.s(slots=True)
class EmbedFooter(DictSerializationMixin):
    """
    Representation of an Embed Footer.

    Attributes:
        text: Footer text
        icon_url: Footer icon url
        proxy_icon_url: Proxy icon url

    """

    text: str = attr.ib()
    icon_url: Optional[str] = attr.ib(default=None)
    proxy_icon_url: Optional[str] = attr.ib(default=None, metadata=no_export_meta)

    def __len__(self):
        return len(self.text)


@attr.s(slots=True)
class EmbedProvider(DictSerializationMixin):
    """
    Represents an embed's provider.

    Note:
        Only used by system embeds, not bots

    Attributes:
        name: Provider name
        url: Provider url

    """

    name: Optional[str] = attr.ib(default=None)
    url: Optional[str] = attr.ib(default=None)


@attr.s(slots=True)
class Embed(DictSerializationMixin):
    """Represents a discord embed object."""

    title: Optional[str] = field(default=None, repr=True)
    """The title of the embed"""
    description: Optional[str] = field(default=None, repr=True)
    """The description of the embed"""
    color: Optional[Union[Color, dict, tuple, list, str, int]] = field(
        default=None, repr=True, metadata=export_converter(process_color)
    )
    """The colour of the embed"""
    url: Optional[str] = field(default=None, validator=v_optional(instance_of(str)), repr=True)
    """The url the embed should direct to when clicked"""
    timestamp: Optional[Timestamp] = field(
        default=None,
        converter=c_optional(timestamp_converter),
        on_setattr=setters.convert,
        validator=v_optional(instance_of((datetime, float, int))),
        repr=True,
    )
    """Timestamp of embed content"""
    fields: List[EmbedField] = field(factory=list, converter=list_converter(EmbedField.from_dict), repr=True)
    """A list of [fields][dis_snek.models.discord_objects.embed.EmbedField] to go in the embed"""
    author: Optional[EmbedAuthor] = field(default=None, converter=c_optional(EmbedAuthor.from_dict))
    """The author of the embed"""
    thumbnail: Optional[EmbedAttachment] = field(default=None, converter=c_optional(EmbedAttachment.from_dict))
    """The thumbnail of the embed"""
    image: Optional[EmbedAttachment] = field(default=None, converter=c_optional(EmbedAttachment.from_dict))
    """The image of the embed"""
    video: Optional[EmbedAttachment] = field(
        default=None, converter=c_optional(EmbedAttachment.from_dict), metadata=no_export_meta
    )
    """The video of the embed, only used by system embeds"""
    footer: Optional[EmbedFooter] = field(default=None, converter=c_optional(EmbedFooter.from_dict))
    """The footer of the embed"""
    provider: Optional[EmbedProvider] = field(
        default=None, converter=c_optional(EmbedProvider.from_dict), metadata=no_export_meta
    )
    """The provider of the embed, only used for system embeds"""

    @title.validator
    def _name_validation(self, attribute: str, value: Any) -> None:
        """Validate the embed title."""
        if value is not None:
            if isinstance(value, str):
                if len(value) > EMBED_MAX_NAME_LENGTH:
                    raise ValueError(f"Title cannot exceed {EMBED_MAX_NAME_LENGTH} characters")
                return
            raise TypeError("Title must be of type String")

    @description.validator
    def _description_validation(self, attribute: str, value: Any) -> None:
        """Validate the description."""
        if value is not None:
            if isinstance(value, str):
                if len(value) > EMBED_MAX_DESC_LENGTH:
                    raise ValueError(f"Description cannot exceed {EMBED_MAX_DESC_LENGTH} characters")
                return
            raise TypeError("Description must be of type String")

    @fields.validator
    def _fields_validation(self, attribute: str, value: Any) -> None:
        """Validate the fields."""
        if isinstance(value, list):
            if len(value) > EMBED_MAX_FIELDS:
                raise ValueError(f"Embeds can only hold {EMBED_MAX_FIELDS} fields")

    def _check_object(self) -> None:
        self._name_validation("title", self.title)
        self._description_validation("description", self.description)
        self._fields_validation("fields", self.fields)

        if len(self) > EMBED_TOTAL_MAX:
            raise ValueError(
                "Your embed is too large, more info at https://discord.com/developers/docs/resources/channel#embed-limits"
            )

    def __len__(self):
        # yes i know there are far more optimal ways to write this
        # its written like this for readability
        total: int = 0
        if self.title:
            total += len(self.title)
        if self.description:
            total += len(self.description)
        if self.footer:
            total += len(self.footer)
        if self.author:
            total += len(self.author)
        if self.fields:
            total += sum(map(len, self.fields))
        return total

    def set_author(
        self,
        name: str,
        url: Optional[str] = None,
        icon_url: Optional[str] = None,
    ) -> None:
        """
        Set the author field of the embed.

        Args:
            name: The text to go in the title section
            url: A url link to the author
            icon_url: A url of an image to use as the icon

        """
        self.author = EmbedAuthor(name=name, url=url, icon_url=icon_url)

    def set_thumbnail(self, url: str) -> None:
        """
        Set the thumbnail of the embed.

        Args:
            url: the url of the image to use

        """
        self.thumbnail = EmbedAttachment(url=url)

    def set_image(self, url: str) -> None:
        """
        Set the image of the embed.

        Args:
            url: the url of the image to use

        """
        self.image = EmbedAttachment(url=url)

    def set_footer(self, text: str, icon_url: Optional[str] = None) -> None:
        """
        Set the footer field of the embed.

        Args:
            text: The text to go in the title section
            icon_url: A url of an image to use as the icon

        """
        self.footer = EmbedFooter(text=text, icon_url=icon_url)

    def add_field(self, name: str, value: Any, inline: bool = False) -> None:
        """
        Add a field to the embed.

        Args:
            name: The title of this field
            value: The value in this field
            inline: Should this field be inline with other fields?

        """
        self.fields.append(EmbedField(name, str(value), inline))
        self._fields_validation("fields", self.fields)


def process_embeds(embeds: Optional[Union[List[Union[Embed, Dict]], Union[Embed, Dict]]]) -> Optional[List[dict]]:
    """
    Process the passed embeds into a format discord will understand.

    Args:
        embeds: List of dict / embeds to process

    """
    if embeds is None:
        # Its just empty, so nothing to process.
        return embeds

    if isinstance(embeds, Embed):
        # Single embed, convert it to dict and wrap it into a list for discord.
        return [embeds.to_dict()]

    if isinstance(embeds, dict):
        # We assume the dict correctly represents a single discord embed and just send it blindly
        # after wrapping it in a list for discord
        return [embeds]

    if isinstance(embeds, list):
        # A list of embeds, convert Embed to dict representation if needed.
        return [embed.to_dict() if isinstance(embed, Embed) else embed for embed in embeds]

    raise ValueError(f"Invalid embeds: {embeds}")
