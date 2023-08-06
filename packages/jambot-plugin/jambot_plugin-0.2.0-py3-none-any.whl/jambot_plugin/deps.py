from collections import namedtuple
from functools import wraps
from typing import Any

import aiodine


STORE = aiodine.Store()

NOT_FOUND_DEP = object()


def dependency(func):  # type: ignore
    return STORE.provider(scope="session")(func)


def consumer(func):  # type: ignore
    return STORE.consumer(func)


async def inject(target: object, *dependencies: str) -> None:
    deps_holder = namedtuple("DepsHolder", dependencies)  # type: ignore

    @wraps(deps_holder)
    async def async_deps_holder(*args: Any) -> deps_holder:
        return deps_holder(*args)

    resolved_deps = await STORE.consumer(async_deps_holder)(
        *([NOT_FOUND_DEP] * len(dependencies)),
    )

    for dep_name in dependencies:
        dep_value = getattr(resolved_deps, dep_name)
        if dep_value is NOT_FOUND_DEP:
            raise RuntimeError(f"Dependency {dep_name} not found")
        else:
            setattr(target, dep_name, dep_value)


async def enter_session() -> None:
    return await STORE.enter_session()


async def exit_session() -> None:
    return await STORE.exit_session()


def freeze() -> None:
    return STORE.freeze()


def reset_store() -> None:
    global STORE
    STORE = aiodine.Store()
