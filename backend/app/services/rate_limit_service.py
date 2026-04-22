from collections import deque
from datetime import datetime, timedelta, timezone

WINDOW_SECONDS = 60
MAX_MESSAGES_PER_WINDOW = 15

_user_message_timestamps: dict[str, deque[datetime]] = {}


def is_rate_limited(user_id: str) -> bool:
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(seconds=WINDOW_SECONDS)

    timestamps = _user_message_timestamps.setdefault(user_id, deque())

    while timestamps and timestamps[0] < window_start:
        timestamps.popleft()

    if len(timestamps) >= MAX_MESSAGES_PER_WINDOW:
        return True

    timestamps.append(now)
    return False