try:
    from mill_bin.version import version as __version__
except ImportError:
    __version__ = "unknown"

from mill_cache import main
source = main.source
