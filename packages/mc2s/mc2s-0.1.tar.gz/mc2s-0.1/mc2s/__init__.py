import sys as _sys
import os as _os


# Look for submodules and add it to the path if available
package_path = _os.path.dirname(_os.path.abspath(__file__))
_submodules_path = _os.path.join(_os.path.dirname(package_path), 'submodules')
if _os.path.exists(_submodules_path):
    for folder in _os.listdir(_submodules_path):
        folder_path = _os.path.join(_submodules_path, folder)
        if _os.path.isdir(folder_path):
            _sys.path.append(folder_path)