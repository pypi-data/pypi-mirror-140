
import contextlib
import io
from typing import (
    Callable,
    Iterator, List, Optional, Union)

from aio.core import functional, output


@contextlib.contextmanager
def buffered(
        stdout: Union[list, io.TextIOWrapper] = None,
        stderr: Union[list, io.TextIOWrapper] = None,
        mangle: Optional[Callable[[list], list]] = None) -> Iterator[None]:
    """Captures stdout and stderr and feeds lines to supplied lists."""

    mangle = mangle or (lambda lines: lines)

    if stdout is None and stderr is None:
        raise output.exceptions.BufferUtilError(
            "You must specify stdout and/or stderr")

    contexts: List[
        Union[
            contextlib.redirect_stderr[io.TextIOWrapper],
            contextlib.redirect_stdout[io.TextIOWrapper]]] = []

    if stdout is not None:
        _stdout = (
            io.TextIOWrapper(io.BytesIO())
            if isinstance(stdout, list)
            else stdout)
        contexts.append(contextlib.redirect_stdout(_stdout))
    if stderr is not None:
        _stderr = (
            io.TextIOWrapper(io.BytesIO())
            if isinstance(stderr, list)
            else stderr)
        contexts.append(contextlib.redirect_stderr(_stderr))

    with functional.nested(*contexts):
        yield

    if isinstance(stdout, list):
        _stdout.seek(0)
        stdout.extend(mangle(_stdout.read().strip().split("\n")))
    if isinstance(stderr, list):
        _stderr.seek(0)
        stderr.extend(mangle(_stderr.read().strip().split("\n")))
