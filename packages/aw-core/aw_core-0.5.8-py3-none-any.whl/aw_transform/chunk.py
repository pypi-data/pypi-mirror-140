import logging
from typing import List, Dict
from datetime import timedelta

from aw_core.models import Event

logger = logging.getLogger(__name__)


def chunk_events_by_key(events: List[Event], key: str) -> List[Event]:
    chunked_events: List[Event] = []
    for event in events:
        if key not in event.data:
            break
        if chunked_events and chunked_events[-1].data[key] == event.data[key]:
            chunked_event = chunked_events[-1]
            chunked_event.duration += event.duration
            chunked_event.data["subevents"].append(event)
        else:
            data = {key: event.data[key], "subevents": [event]}
            chunked_event = Event(
                timestamp=event.timestamp, duration=event.duration, data=data
            )
            chunked_events.append(chunked_event)

    return chunked_events


def chunk_by_hour(events: List[Event]) -> List[Event]:
    ...
