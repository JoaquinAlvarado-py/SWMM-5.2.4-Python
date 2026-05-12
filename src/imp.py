# -*- coding: utf-8 -*-
"""Compatibility shim for the removed 'imp' module (Python >= 3.12).

Only implements find_module / load_module used by frmMain plugin loader.
"""
import importlib.util
from importlib.machinery import ModuleSpec
import sys
import types


def find_module(name, path=None):
    """Locate a module in the given path, return (file, pathname, description).

    Returns a tuple that can be unpacked into load_module's positional args,
    matching the legacy imp.find_module signature.
    """
    if path:
        for p in path:
            init_path = f"{p}/{name}.py"
            spec = importlib.util.spec_from_file_location(
                name, init_path,
                submodule_search_locations=[p],
            )
            if spec is not None:
                return (None, p, spec)
    spec = importlib.util.find_spec(name)
    if spec is None:
        raise ImportError(f"No module named {name!r}")
    return (None, spec.origin, spec)


def load_module(name, file, pathname, description):
    """Load a module from the info returned by find_module.

    *description* is actually the importlib ModuleSpec when coming from
    our shim's find_module.
    """
    if isinstance(description, ModuleSpec) or hasattr(description, 'loader'):
        spec = description
    else:
        # Build a spec from pathname (folder containing __init__.py)
        init_path = f"{pathname}/{name}.py"
        spec = importlib.util.spec_from_file_location(
            name, init_path,
            submodule_search_locations=[pathname],
        )
    if spec is None:
        raise ImportError(f"Cannot load module {name!r} from {pathname!r}")
    module = importlib.util.module_from_spec(spec)
    # Register in sys.modules so relative imports work inside the plugin
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
