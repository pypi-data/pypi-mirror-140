from dataclasses import dataclass

__version__ = "2.0.5"


@dataclass
class VersionInfo:
    major: int
    minor: int
    micro: int
    releaselevel: str
    serial: int


version_info = VersionInfo(1, 1, 3, "stable", 0)
