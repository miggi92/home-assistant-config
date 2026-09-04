"""Media Player entity for Voice Satellite.

Exposes a media_player entity on the satellite device so HA can target
browser tablets with tts.speak, media_player.play_media, and
media_player.media_announce service calls.

Commands are pushed to the card via the satellite event subscription.
The card reports playback state back via a WS command, and the entity
updates HA state accordingly.
"""

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import unquote

from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
    async_process_play_media_url,
)
from homeassistant.components.media_source import (
    async_browse_media as ms_browse,
    async_resolve_media,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.network import NoURLAvailableError
from homeassistant.helpers.restore_state import ExtraStoredData, RestoreEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .media_proxy import register_proxied_url

_LOGGER = logging.getLogger(__name__)

# Browse results are remembered so play_media can attach a title and
# artwork to whatever the user picked. Bounded so a long browsing
# session can't grow it without limit.
_BROWSE_CACHE_LIMIT = 500

# Local media source ids look like
# media-source://media_source/local/Music/Artist/Song.mp3
_LOCAL_MEDIA_PREFIX = "media-source://media_source/"


class MediaPlayerExtraData(ExtraStoredData):
    """Extra stored data for persisting volume across reboots."""

    def __init__(self, volume_level: float, is_volume_muted: bool) -> None:
        """Initialize extra data."""
        self.volume_level = volume_level
        self.is_volume_muted = is_volume_muted

    def as_dict(self) -> dict[str, Any]:
        """Serialize to dict."""
        return {
            "volume_level": self.volume_level,
            "is_volume_muted": self.is_volume_muted,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MediaPlayerExtraData:
        """Deserialize from dict."""
        return cls(
            volume_level=data.get("volume_level", 1.0),
            is_volume_muted=data.get("is_volume_muted", False),
        )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the media player entity from a config entry."""
    entity = VoiceSatelliteMediaPlayer(entry)
    async_add_entities([entity])

    # Store for WS handler lookup
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][f"{entry.entry_id}_media_player"] = entity


class VoiceSatelliteMediaPlayer(MediaPlayerEntity, RestoreEntity):
    """A media player representing a browser satellite's audio output."""

    _attr_has_entity_name = True
    _attr_translation_key = "media_player"
    _attr_device_class = MediaPlayerDeviceClass.TV
    _attr_supported_features = (
        MediaPlayerEntityFeature.PLAY_MEDIA
        | MediaPlayerEntityFeature.MEDIA_ANNOUNCE
        | MediaPlayerEntityFeature.BROWSE_MEDIA
        | MediaPlayerEntityFeature.PLAY
        | MediaPlayerEntityFeature.PAUSE
        | MediaPlayerEntityFeature.STOP
        | MediaPlayerEntityFeature.SEEK
        | MediaPlayerEntityFeature.VOLUME_SET
        | MediaPlayerEntityFeature.VOLUME_MUTE
    )

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the media player entity."""
        self._entry = entry
        self._satellite_name: str = entry.data["name"]
        self._attr_unique_id = f"{entry.entry_id}_media_player"

        self._attr_state = MediaPlayerState.IDLE
        self._attr_volume_level = 1.0
        self._attr_is_volume_muted = False
        self._attr_media_content_id: str | None = None
        self._attr_media_content_type: str | None = None
        self._attr_media_position: float | None = None
        self._attr_media_duration: int | None = None
        self._attr_media_position_updated_at = None
        self._attr_media_title: str | None = None
        self._attr_media_artist: str | None = None
        self._attr_media_album_name: str | None = None
        self._attr_media_image_url: str | None = None

        # media_content_id -> {"title": ..., "thumbnail": ...} for items
        # seen in browse results. See _resolve_metadata.
        self._browse_cache: dict[str, dict[str, str | None]] = {}

    @property
    def extra_restore_state_data(self) -> MediaPlayerExtraData:
        """Return extra data to persist across reboots."""
        return MediaPlayerExtraData(
            self._attr_volume_level,
            self._attr_is_volume_muted,
        )

    async def async_added_to_hass(self) -> None:
        """Restore volume and mute state on startup."""
        await super().async_added_to_hass()
        extra_data = await self.async_get_last_extra_data()
        if extra_data:
            data = MediaPlayerExtraData.from_dict(extra_data.as_dict())
            self._attr_volume_level = data.volume_level
            self._attr_is_volume_muted = data.is_volume_muted

    @property
    def available(self) -> bool:
        """Available when the satellite has an active card connection."""
        satellite = self._get_satellite_entity()
        if satellite is None:
            return False
        return satellite.available

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device info - same device as the satellite entity."""
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
        }

    def _get_satellite_entity(self):
        """Lazy-lookup the satellite entity for pushing events."""
        return self.hass.data.get(DOMAIN, {}).get(self._entry.entry_id)

    def _push_command(self, command: str, **kwargs: Any) -> None:
        """Push a media_player command to the card via satellite subscription."""
        satellite = self._get_satellite_entity()
        if satellite is None:
            _LOGGER.warning(
                "Cannot push media_player command - satellite entity not found for '%s'",
                self._satellite_name,
            )
            return

        payload = {"command": command, **kwargs}
        satellite._push_satellite_event("media_player", payload)
        _LOGGER.debug(
            "Media player command pushed for '%s': %s",
            self._satellite_name,
            payload,
        )

    async def async_browse_media(
        self,
        media_content_type: MediaType | str | None = None,
        media_content_id: str | None = None,
    ):
        """Delegate media browsing to media_source, filtered to playable types.

        Accepts audio, video, HLS streams (cameras with STREAM support), and
        MJPEG / snapshot cameras. HA's camera media source emits HLS for
        cameras that support streaming, and falls back to camera.content_type
        (image/jpeg or multipart/x-mixed-replace) for the rest, served as a
        continuous MJPEG via /api/camera_proxy_stream.
        """
        def _is_playable(item) -> bool:
            ct = (item.media_content_type or "").lower()
            return (
                ct.startswith("audio/")
                or ct.startswith("video/")
                or ct.startswith("image/")
                or ct.startswith("multipart/x-mixed-replace")
                or ct == "application/vnd.apple.mpegurl"
                or ct == "application/x-mpegurl"
            )

        result = await ms_browse(
            self.hass,
            media_content_id,
            content_filter=_is_playable,
        )
        self._remember_browse_result(result)
        return result

    def _remember_browse_result(self, item) -> None:
        """Record titles and thumbnails of browsed items for later playback.

        HA's media browser only sends the content id and type to
        play_media, so this is the only way to know what the user picked
        when they choose something through the UI. Radio stations,
        podcasts and most third party sources carry artwork here.
        """
        items = [item, *(item.children or [])]
        for entry in items:
            if entry.can_expand or not entry.media_content_id:
                continue
            self._browse_cache[entry.media_content_id] = {
                "title": entry.title,
                "thumbnail": entry.thumbnail,
            }
        while len(self._browse_cache) > _BROWSE_CACHE_LIMIT:
            self._browse_cache.pop(next(iter(self._browse_cache)))

    def _resolve_metadata(
        self, media_id: str, extra: dict[str, Any] | None
    ) -> dict[str, str | None]:
        """Work out title, artist, album and artwork for a play_media call.

        Sources, in order of preference:
          1. ``extra.metadata`` or top level ``extra`` keys on the service
             call (the Cast convention: title, artist, album, thumb).
          2. The browse result the user picked the item from.
          3. The file name, for local media library files.
        """
        meta: dict[str, Any] = {}
        if isinstance(extra, dict):
            nested = extra.get("metadata")
            for source in (extra, nested if isinstance(nested, dict) else {}):
                for key in ("title", "artist", "album", "album_name",
                            "thumbnail", "thumb", "image_url", "images"):
                    if source.get(key) not in (None, ""):
                        meta[key] = source[key]

        title = meta.get("title")
        artist = meta.get("artist")
        album = meta.get("album") or meta.get("album_name")
        image = meta.get("thumbnail") or meta.get("thumb") or meta.get("image_url")
        images = meta.get("images")
        if not image and isinstance(images, list) and images:
            first = images[0]
            image = first.get("url") if isinstance(first, dict) else first

        cached = self._browse_cache.get(media_id)
        if cached:
            title = title or cached.get("title")
            image = image or cached.get("thumbnail")

        if not title and media_id.startswith(_LOCAL_MEDIA_PREFIX):
            name = unquote(media_id).rstrip("/").rsplit("/", 1)[-1]
            title = name.rsplit(".", 1)[0] if "." in name else name

        return {
            "title": title or None,
            "artist": artist or None,
            "album": album or None,
            "image": self._absolute_image_url(image),
        }

    def _absolute_image_url(self, url: Any) -> str | None:
        """Turn a thumbnail reference into a URL HA's image proxy can fetch.

        Relative HA paths (camera snapshots, media source proxies) need a
        signature and an absolute base, which is what the media_player
        helper does. Anything already absolute passes through.
        """
        if not isinstance(url, str) or not url:
            return None
        if url.startswith(("http://", "https://")):
            return url
        if not url.startswith("/"):
            return None
        try:
            return async_process_play_media_url(self.hass, url)
        except (ValueError, NoURLAvailableError) as err:
            _LOGGER.debug(
                "Cannot build artwork URL for '%s' from %s: %s",
                self._satellite_name, url, err,
            )
            return None

    def _clear_media_metadata(self) -> None:
        """Drop everything that describes the current item."""
        self._attr_media_content_id = None
        self._attr_media_content_type = None
        self._attr_media_position = None
        self._attr_media_duration = None
        self._attr_media_position_updated_at = None
        self._attr_media_title = None
        self._attr_media_artist = None
        self._attr_media_album_name = None
        self._attr_media_image_url = None

    async def async_play_media(
        self,
        media_type: MediaType | str,
        media_id: str,
        **kwargs: Any,
    ) -> None:
        """Play media on the browser satellite."""
        # Camera entities are pushed unresolved (entity_id, type "camera")
        # so the browser can negotiate WebRTC over its authenticated WS
        # connection (camera/webrtc/offer) for sub-second latency. The
        # frontend checks camera/capabilities itself and falls back to
        # resolving the HLS / MJPEG URL when WebRTC isn't available.
        metadata = self._resolve_metadata(media_id, kwargs.get("extra"))

        camera_entity: str | None = None
        if media_id.startswith("media-source://camera/"):
            camera_entity = media_id.removeprefix("media-source://camera/")
        elif media_id.startswith("camera."):
            camera_entity = media_id

        if camera_entity is not None:
            media_id = camera_entity
            media_type = "camera"
        # Resolve remaining media-source:// URIs to actual playable URLs
        elif media_id.startswith("media-source://"):
            result = await async_resolve_media(
                self.hass, media_id, self.entity_id
            )
            media_id = result.url
            media_type = result.mime_type

        # Plain-HTTP sources (e.g. Music Assistant's stream server, which
        # is HTTP-only by design) get blocked as mixed content when the
        # panel is loaded over HTTPS.  We offer a same-origin proxy path
        # as an alternative, but whether it's needed depends on the page
        # scheme - which only the browser knows (HA may be reachable over
        # both http and https).  So we always provide `proxy_url` for
        # http upstreams and let the frontend use it only when its page
        # is actually HTTPS; an all-HTTP setup plays the direct URL and
        # skips the needless relay through HA.
        proxy_url = None
        if isinstance(media_id, str) and media_id.startswith("http://"):
            proxy_url = register_proxied_url(self.hass, media_id)

        announce = kwargs.get("announce")
        self._push_command(
            "play",
            media_id=media_id,
            media_type=str(media_type),
            announce=announce,
            volume=self._attr_volume_level,
            proxy_url=proxy_url,
        )

        # Optimistic state update (keep the original URL on the entity)
        self._clear_media_metadata()
        self._attr_state = MediaPlayerState.PLAYING
        self._attr_media_content_id = media_id
        self._attr_media_content_type = str(media_type)
        self._attr_media_title = metadata["title"]
        self._attr_media_artist = metadata["artist"]
        self._attr_media_album_name = metadata["album"]
        self._attr_media_image_url = metadata["image"]
        self.async_write_ha_state()

    async def async_media_pause(self) -> None:
        """Pause playback."""
        self._push_command("pause")
        self._attr_state = MediaPlayerState.PAUSED
        self.async_write_ha_state()

    async def async_media_play(self) -> None:
        """Resume playback."""
        self._push_command("resume")
        self._attr_state = MediaPlayerState.PLAYING
        self.async_write_ha_state()

    async def async_media_stop(self) -> None:
        """Stop playback."""
        self._push_command("stop")
        self._attr_state = MediaPlayerState.IDLE
        self._clear_media_metadata()
        self.async_write_ha_state()

    async def async_media_seek(self, position: float) -> None:
        """Seek to a position in seconds.

        The browser reports the settled position back once the element
        has actually moved, which corrects the optimistic value below.
        """
        self._push_command("seek", position=position)
        self._attr_media_position = position
        self._attr_media_position_updated_at = dt_util.utcnow()
        self.async_write_ha_state()

    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level (0-1)."""
        self._push_command("volume_set", volume=volume)
        self._attr_volume_level = volume
        self.async_write_ha_state()

    async def async_mute_volume(self, mute: bool) -> None:
        """Mute or unmute."""
        self._push_command("volume_mute", mute=mute)
        self._attr_is_volume_muted = mute
        self.async_write_ha_state()

    @callback
    def update_playback_state(
        self,
        state: str,
        volume: float | None = None,
        media_id: str | None = None,
        position: float | None = None,
        duration: float | None = None,
    ) -> None:
        """Update state from card's WS report."""
        state_map = {
            "playing": MediaPlayerState.PLAYING,
            "paused": MediaPlayerState.PAUSED,
            "idle": MediaPlayerState.IDLE,
        }
        mapped = state_map.get(state)
        if mapped is not None:
            self._attr_state = mapped

        if volume is not None:
            self._attr_volume_level = volume

        if media_id is not None:
            self._attr_media_content_id = media_id
        elif mapped == MediaPlayerState.IDLE:
            self._clear_media_metadata()

        # Position and duration only arrive for seekable media. Live
        # streams and images send neither, so nothing is invented here.
        if position is not None and mapped != MediaPlayerState.IDLE:
            self._attr_media_position = position
            self._attr_media_position_updated_at = dt_util.utcnow()
        if duration is not None and mapped != MediaPlayerState.IDLE:
            self._attr_media_duration = int(round(duration))

        self.async_write_ha_state()
        _LOGGER.debug(
            "Media player state updated for '%s': %s",
            self._satellite_name,
            state,
        )
