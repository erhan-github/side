import platform
import subprocess
import logging

logger = logging.getLogger(__name__)

class HardwareIntelligence:
    """
    [INTEL-5] Detects hardware capabilities to select the 'Perfection Path'.
    Supports macOS (Apple Silicon), Linux, and Windows.
    """

    @staticmethod
    def get_capabilities() -> dict:
        caps = {
            "os": platform.system(),
            "arch": platform.machine(),
            "neon": False,
            "avx2": False,
            "avx512": False,
            "popcnt": hasattr(int, "bit_count") # Native Python 3.10+
        }

        if caps["os"] == "Darwin":
            # macOS check
            try:
                output = subprocess.check_output(["sysctl", "-a"]).decode()
                caps["neon"] = "hw.optional.neon: 1" in output or "arm64" in caps["arch"].lower()
            except: pass
        
        elif caps["os"] == "Linux":
            # Linux check
            try:
                with open("/proc/cpuinfo", "r") as f:
                    cpuinfo = f.read()
                    caps["avx2"] = "avx2" in cpuinfo
                    caps["avx512"] = "avx512" in cpuinfo
                    caps["neon"] = "asimd" in cpuinfo or "neon" in cpuinfo
            except: pass

        elif caps["os"] == "Windows":
            # Windows (Basic arch check)
            caps["avx2"] = "AMD64" in caps["arch"] # Simplified for now
            
        return caps

    @staticmethod
    def select_strategy() -> str:
        """Determines the optimal search strategy for the current device."""
        caps = HardwareIntelligence.get_capabilities()
        
        if caps["neon"]:
            return "NEON_ACCELERATED"
        elif caps["avx512"]:
            return "AVX512_ACCELERATED"
        elif caps["avx2"]:
            return "AVX2_ACCELERATED"
        elif caps["popcnt"]:
            return "PYTHON_NATIVE_POPCNT"
        else:
            return "SOFTWARE_FALLBACK"

hardware_intel = HardwareIntelligence()
