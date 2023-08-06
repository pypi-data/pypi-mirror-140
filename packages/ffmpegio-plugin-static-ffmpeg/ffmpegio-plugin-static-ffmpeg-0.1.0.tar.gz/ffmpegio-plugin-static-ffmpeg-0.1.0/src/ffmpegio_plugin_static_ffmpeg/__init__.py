"""ffmpegio plugin to use `numpy.ndarray` objects for media data I/O"""
import logging
from pluggy import HookimplMarker
from static_ffmpeg import run

hookimpl = HookimplMarker("ffmpegio")

__version__ = "0.1.0"
__all__ = ["finder"]


@hookimpl
def finder():
    """find ffmpeg and ffprobe executables"""

    try:
        paths = run.get_or_fetch_platform_executables_else_raise()
    except Exception as e:
        logging.warn(
            f"""ffmpegio-plugin-static-ffmpeg plugin package is detected but the FFmpeg executables were not found. Error message:
            
              {e}"""
        )
        return None

    return paths
