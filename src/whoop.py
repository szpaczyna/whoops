import logging
import secrets
import threading
import urllib.parse
from datetime import datetime, timedelta, timezone
from typing import Callable, Dict, List, Optional, Type

import requests
from flask import current_app

from src.models import Model
from src.models.cycle import WhoopCycle
from src.models.recovery import WhoopRecovery
from src.models.sleep import WhoopSleep
from src.models.workout import WhoopWorkout

API_ENDPOINT = "https://api.prod.whoop.com/"
API_VERSION = "developer/v2"
PAGE_LIMIT = 25
HTTP_TIMEOUT = 30
DEFAULT_EXPIRES_IN = 3600
# refresh_token_job runs every 5 minutes, so a 10 minute margin refreshes 5-10 minutes before expiry.
REFRESH_MARGIN = timedelta(minutes=10)


logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _as_utc(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


class WhoopClient:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        on_refresh: Optional[Callable[["WhoopClient"], None]] = None,
    ):
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self.tokens: Dict = {}
        self.refreshed_at: datetime = _utcnow()
        self.on_refresh = on_refresh
        # WHOOP rotates refresh tokens, so two concurrent refreshes would invalidate each other.
        self._lock = threading.RLock()

    def set_tokens(self, auth_code: str) -> None:
        """Exchange authorization code for tokens."""
        params = self._build_token_params(
            grant_type="authorization_code",
            code=auth_code,
            redirect_uri=current_app.config["REDIRECT_URI"],
        )
        tokens = self._post_token_request(params)
        with self._lock:
            self.tokens = tokens
            self.refreshed_at = _utcnow()

    def needs_refresh(self) -> bool:
        """Check if the token expires within REFRESH_MARGIN."""
        if not self.tokens:
            return True

        expires_in = self.tokens.get("expires_in") or DEFAULT_EXPIRES_IN
        expires_at = _as_utc(self.refreshed_at) + timedelta(seconds=expires_in)
        return _utcnow() >= expires_at - REFRESH_MARGIN

    def refresh_token(self):
        """Refresh the access token unconditionally."""
        with self._lock:
            params = self._build_token_params(
                grant_type="refresh_token",
                refresh_token=self.tokens.get("refresh_token"),
                scope="offline",
            )

            self.tokens = self._post_token_request(params)
            self.refreshed_at = _utcnow()

            if self.on_refresh:
                self.on_refresh(self)

    def ensure_fresh_token(self) -> bool:
        """Refresh the token if it is close to expiry. Returns True if refreshed."""
        if not self.tokens or not self.needs_refresh():
            return False

        with self._lock:
            if not self.needs_refresh():
                return False
            self.refresh_token()
            return True

    def authorization_url(self):
        """Build the OAuth authorization URL."""
        state = secrets.token_urlsafe(16)
        current_app.config["OAuthState"] = state

        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": current_app.config["REDIRECT_URI"],
            "scope": "offline read:workout read:recovery read:sleep read:cycles read:profile read:body_measurement",
            "state": state,
        }
        query = urllib.parse.urlencode(params)
        return f"{API_ENDPOINT}oauth/oauth2/auth?{query}"

    def get_cycles(self, start: Optional[datetime] = None) -> List[WhoopCycle]:
        return self._fetch_paginated("cycle", WhoopCycle, start)

    def get_sleeps(self, start: Optional[datetime] = None) -> List[WhoopSleep]:
        return self._fetch_paginated("activity/sleep", WhoopSleep, start, scored_only=True)

    def get_recoveries(self, start: Optional[datetime] = None) -> List[WhoopRecovery]:
        return self._fetch_paginated("recovery", WhoopRecovery, start, scored_only=True)

    def get_workouts(self, start: Optional[datetime] = None) -> List[WhoopWorkout]:
        return self._fetch_paginated("activity/workout", WhoopWorkout, start)

    def get_profile_basic(self) -> Dict:
        return self._get("user/profile/basic")

    def get_body_measurement(self) -> Dict:
        return self._get("user/measurement/body")

    def _fetch_paginated(
        self,
        endpoint: str,
        model_cls: Type[Model],
        start: Optional[datetime] = None,
        scored_only: bool = False,
    ) -> List[Model]:
        """Generic method to fetch paginated data from the Whoop API."""
        url = f"{API_ENDPOINT}{API_VERSION}/{endpoint}"
        params: Dict = {"limit": PAGE_LIMIT}
        if start is not None:
            params["start"] = _as_utc(start).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        results: List[Model] = []

        while True:
            response = requests.get(url, headers=self._auth_header(), params=dict(params), timeout=HTTP_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            records = data.get("records", [])
            if scored_only:
                records = [r for r in records if r.get("score_state") == "SCORED"]
            results.extend(model_cls.from_json(r) for r in records)

            next_token = data.get("next_token")
            if not next_token:
                return results
            params["nextToken"] = next_token

    def _get(self, endpoint: str) -> Dict:
        """Generic single-resource GET against the Whoop API v2."""
        url = f"{API_ENDPOINT}{API_VERSION}/{endpoint}"
        response = requests.get(url, headers=self._auth_header(), timeout=HTTP_TIMEOUT)
        response.raise_for_status()
        return response.json()

    def _post_token_request(self, data: Dict) -> Dict:
        """Internal helper to post to the token endpoint."""
        url = f"{API_ENDPOINT}oauth/oauth2/token"
        response = requests.post(url, data=data, timeout=HTTP_TIMEOUT)
        response.raise_for_status()
        return response.json()

    def _build_token_params(self, **overrides) -> Dict:
        """Base token params with overrides."""
        base = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        base.update(overrides)
        return base

    def _auth_header(self) -> Dict:
        with self._lock:
            self.ensure_fresh_token()
            if self.tokens:
                return {"Authorization": f"Bearer {self.tokens['access_token']}"}
            return {}
