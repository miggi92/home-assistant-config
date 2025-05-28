from datetime import datetime, timezone, timedelta
from typing import Any, Optional
import logging
from .base_sensor import HandballBaseSensor
from ..const import DOMAIN
from ..api import HandballNetAPI

_LOGGER = logging.getLogger(__name__)

class HandballLiveTickerEventsSensor(HandballBaseSensor):
    def __init__(self, hass, entry, team_id, api: HandballNetAPI):
        super().__init__(hass, entry, team_id)
        self._api = api
        self._attr_name = f"Handball Live Ticker {team_id}"
        self._attr_unique_id = f"handball_live_ticker_events_{team_id}"
        self._attr_icon = "mdi:television-play"
        self._attr_should_poll = False
        self._state = "Kein Live-Spiel"
        self._attributes = {}

    @property
    def state(self) -> str:
        return self._state

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return self._attributes

    def get_current_live_game(self) -> Optional[dict]:
        """Find currently running game"""
        matches = self.hass.data.get(DOMAIN, {}).get(self._team_id, {}).get("matches", [])
        now = datetime.now(timezone.utc)
        
        for match in matches:
            ts = match.get("startsAt")
            if not isinstance(ts, int):
                continue
            try:
                start = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
                end = start + timedelta(hours=2)
            except Exception:
                continue
            
            if start <= now <= end:
                return match
        return None

    async def async_update_live_ticker(self) -> None:
        """Update live ticker data"""
        current_game = self.get_current_live_game()
        
        if not current_game:
            self._state = "Kein Live-Spiel"
            self._attributes = {
                "game_state": "no_live_game",
                "last_updated": datetime.now().isoformat()
            }
            return

        game_id = current_game.get("id")
        if not game_id:
            _LOGGER.warning("No game ID found for current game")
            return

        try:
            live_data = await self._api.get_live_ticker(game_id)
            if not live_data:
                _LOGGER.warning("No live ticker data received for game %s", game_id)
                return

            summary = live_data.get("summary", {})
            events = live_data.get("events", [])
            
            # Get current score and game state
            home_goals = summary.get("homeGoals", 0)
            away_goals = summary.get("awayGoals", 0)
            game_state = summary.get("state", "Unknown")
            home_team = summary.get("homeTeam", {}).get("name", "Home")
            away_team = summary.get("awayTeam", {}).get("name", "Away")
            
            # Current state as text
            if game_state == "Live":
                self._state = f"🔴 LIVE: {home_team} {home_goals}:{away_goals} {away_team}"
            elif game_state == "Post":
                self._state = f"✅ Beendet: {home_team} {home_goals}:{away_goals} {away_team}"
            elif game_state == "Pre":
                self._state = f"⏰ Bald: {home_team} vs {away_team}"
            else:
                self._state = f"{home_team} vs {away_team}"

            # Get latest events (last 10)
            latest_events = []
            for event in events[:10]:  # First 10 events (newest first)
                event_data = {
                    "type": event.get("type", "Unknown"),
                    "time": event.get("time", ""),
                    "message": event.get("message", ""),
                    "score": event.get("score", ""),
                    "team": event.get("team", ""),
                    "timestamp": event.get("timestamp", 0)
                }
                latest_events.append(event_data)

            # Get half-time scores
            home_goals_half = summary.get("homeGoalsHalf")
            away_goals_half = summary.get("awayGoalsHalf")

            self._attributes = {
                "game_id": game_id,
                "game_state": game_state,
                "home_team": home_team,
                "away_team": away_team,
                "home_goals": home_goals,
                "away_goals": away_goals,
                "home_goals_half": home_goals_half,
                "away_goals_half": away_goals_half,
                "field": summary.get("field", {}).get("name", ""),
                "starts_at": summary.get("startsAt"),
                "latest_events": latest_events,
                "total_events": len(events),
                "last_updated": datetime.now().isoformat(),
                "last_event": latest_events[0] if latest_events else None
            }

        except Exception as e:
            _LOGGER.error("Error updating live ticker for game %s: %s", game_id, e)
            self._state = "Fehler beim Laden"
            self._attributes = {
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }
