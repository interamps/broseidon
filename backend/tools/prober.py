# prober.py
import os
import importlib
import inspect
import typing

TOOLS_DIR = os.path.dirname(__file__)
EXCLUDE = {"prober.py", "rag.py", "__init__.py"}
_TYPE_MAP = {"str": "string", "int": "integer", "float": "number", "bool": "boolean", "list": "array", "dict": "object"}


def _type_name(ann) -> str:
    if ann is inspect._empty:
        return "str"
    origin = typing.get_origin(ann)
    return (origin or ann).__name__ if hasattr(origin or ann, "__name__") else "str"


def scan() -> list[dict]:
    """Introspect backend/tools/, return every public function's module, name, params, doc."""
    out = []
    for fname in sorted(os.listdir(TOOLS_DIR)):
        if not fname.endswith(".py") or fname in EXCLUDE:
            continue
        mod_name = fname[:-3]
        try:
            mod = importlib.import_module(f"backend.tools.{mod_name}")
        except Exception as e:
            out.append({"module": mod_name, "error": str(e)})
            continue
        for name, fn in inspect.getmembers(mod, inspect.isfunction):
            if name.startswith("_") or fn.__module__ != mod.__name__:
                continue
            params = {
                pname: {"type": _type_name(p.annotation), "required": p.default is inspect._empty}
                for pname, p in inspect.signature(fn).parameters.items()
            }
            out.append({"module": mod_name, "name": name, "doc": inspect.getdoc(fn) or "", "params": params})
    return out


def to_tool_schemas(entries: list[dict]) -> list[dict]:
    """scan() output -> OpenAI tool schema. Drops fns w/ non-JSON param types."""
    schemas = []
    for e in entries:
        if "error" in e:
            continue
        props, required, skip = {}, [], False
        for pname, meta in e["params"].items():
            jt = _TYPE_MAP.get(meta["type"])
            if jt is None:
                skip = True
                break
            props[pname] = {"type": jt}
            if meta["required"]:
                required.append(pname)
        if skip:
            continue
        schemas.append({
            "type": "function",
            "function": {
                "name": f'{e["module"]}__{e["name"]}',
                "description": e["doc"],
                "parameters": {"type": "object", "properties": props, "required": required},
            },
        })
    return schemas


def run(module: str, name: str, **kwargs):
    """Execute a discovered function by module+name."""
    mod = importlib.import_module(f"backend.tools.{module}")
    return getattr(mod, name)(**kwargs)