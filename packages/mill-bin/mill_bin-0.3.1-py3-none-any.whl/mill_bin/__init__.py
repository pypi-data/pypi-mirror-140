try:
    from mill_bin.version import version as __version__
except ImportError:
    __version__ = "unknown"

from mill_bin import main
source = main.source
