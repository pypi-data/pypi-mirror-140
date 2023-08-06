# language=Markdown
"""
Typing Wrapper -- forward-compatibility for the Python `typing` module.

## Typing Wrapper

This module provides forwards-compatibility for the Python `typing` module.
It contains no actual members on the latest version of Python.
However, even these definitions are not available in the earlier Pythons,
the majority of IDEs' bundled type checkers process them as if they are.
"""

try: from typing import Final
except ImportError:
    from typing_extensions import Final

try: from typing import final
except ImportError:
    from typing_extensions import final
