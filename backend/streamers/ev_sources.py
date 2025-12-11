"""KashRock EV data sources registry for internal EV providers."""

from typing import Dict, Type, List
from streamers.rotowire import RotowireStreamer
from streamers.walter import WalterStreamer
from streamers.proply import ProplyStreamer
from streamers.sharp_props import SharpPropsStreamer
import structlog

logger = structlog.get_logger()

# KashRock EV Sources Registry - internal EV data providers
EV_SOURCES: Dict[str, Type] = {
    "walter": WalterStreamer,
    "rotowire": RotowireStreamer,
    "proply": ProplyStreamer,
    "sharp_props": SharpPropsStreamer,
}

def get_ev_source_streamers() -> List[str]:
    """Get list of available KashRock EV source streamers."""
    return list(EV_SOURCES.keys())

def create_ev_streamer(source_name: str, config: Dict) -> any:
    """Create a KashRock EV streamer instance."""
    if source_name not in EV_SOURCES:
        raise ValueError(f"Unknown KashRock EV source: {source_name}")

    streamer_class = EV_SOURCES[source_name]
    return streamer_class(source_name, config)

# Default KashRock EV sources to run
DEFAULT_EV_SOURCES = [
    "walter",
    "rotowire",
    "proply",
    "sharp_props",
]
