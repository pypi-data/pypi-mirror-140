import inspect
from typing import Any, Awaitable, Callable, Optional, TypeVar, Union, cast

from jetpack import utils
from jetpack._task.errors import NotAsyncError
from jetpack._task.jetpack_function import JetpackFunction
from jetpack._task.jetpack_function_with_client import schedule as schedule
from jetpack.config import symbols

T = TypeVar("T")


# @function is our general remote work decorator. It does not specify how the
# work will be done (RPC, job, queue, etc) and instead leaves that as an
# implementation detail.
def jetroutine_decorator(
    fn: Optional[Callable[..., T]] = None, *, with_checkpointing: bool = False
) -> Union[
    Callable[..., Awaitable[T]],
    Callable[[Callable[..., T]], Callable[..., Awaitable[T]]],
]:
    def wrapper(fn: Callable[..., T]) -> Callable[..., Awaitable[T]]:
        # Use asyncio.iscoroutine() instead?
        if not inspect.iscoroutinefunction(fn):
            raise NotAsyncError(
                f"Jetpack functions must be async. {utils.qualified_func_name(fn)} is not async."
            )
        symbols.get_symbol_table().register(fn)
        task: JetpackFunction[T] = JetpackFunction(fn, with_checkpointing)
        return task

    return wrapper(fn) if fn else wrapper


function = jetroutine_decorator
jet = jetroutine_decorator
jetroutine = jetroutine_decorator
