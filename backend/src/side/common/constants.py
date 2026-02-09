from enum import Enum

class Origin(str, Enum):
    """Source origin of data or intelligence."""
    LOCAL = "local"
    CLOUD = "cloud"
    NETWORK = "network"
    HYBRID = "hybrid"

class Outcome(str, Enum):
    """Outcome of a forensic transaction."""
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    UNKNOWN = "UNKNOWN"
