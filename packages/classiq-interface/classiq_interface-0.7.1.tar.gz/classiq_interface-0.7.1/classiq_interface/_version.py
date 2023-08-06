import sys


def package_version(package: str) -> str:
    try:
        if sys.version_info >= (3, 8):
            from importlib import metadata
        else:
            import importlib_metadata as metadata
    except ImportError:
        raise RuntimeError(
            "Version number unavailable. importlib-metadata is required for Python 3.7"
        )

    return metadata.version(package)


VERSION = package_version(__name__.split(".")[0])
