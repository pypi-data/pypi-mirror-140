import sys as _sys
import os as _os


# Look for submodules and add it to the path if available
package_path = _os.path.dirname(_os.path.abspath(__file__))
_sys.path.append(package_path)