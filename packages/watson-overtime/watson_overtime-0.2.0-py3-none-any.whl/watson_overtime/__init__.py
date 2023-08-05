try:
    import importlib.metadata

    version = importlib.metadata.version(__name__)
except ImportError:
    import importlib_metadata

    version = importlib_metadata.version(__name__)

__version__ = version
