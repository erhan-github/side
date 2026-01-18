"""
DEPRECATED: This module has been refactored into the `cso_ai.tools` package.

For new code, use:
    from cso_ai.tools import TOOLS, handle_tool_call

This file is kept for backwards compatibility but will be removed in a future version.
"""

# Backwards compatibility - re-export from new package
from cso_ai.tools import TOOLS, handle_tool_call

__all__ = ["TOOLS", "handle_tool_call"]

# Emit deprecation warning on import
import warnings
warnings.warn(
    "tools_refined module is deprecated. Use 'from cso_ai.tools import TOOLS, handle_tool_call' instead.",
    DeprecationWarning,
    stacklevel=2
)
