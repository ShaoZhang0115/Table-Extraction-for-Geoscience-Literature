import importlib
import pkgutil

from fastapi import APIRouter

router = APIRouter()

for _, name, is_pkg in pkgutil.iter_modules(path=__path__):
    if is_pkg:
        module = f"{__name__}.{name}"
        module = importlib.import_module(module)
        if "router" in dir(module):
            prefix = f"/{name}"
            router.include_router(module.router, prefix=prefix, tags=[name])
