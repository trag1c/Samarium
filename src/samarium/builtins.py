from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from re import compile
from time import sleep as _sleep
from time import time_ns
from types import GeneratorType
from typing import Any, TypeVar

from samarium.classes import (
    MISSING,
    NULL,
    Array,
    Attrs,
    Null,
    Num,
    Number,
    Slice,
    String,
    correct_type,
    to_string,
)
from samarium.exceptions import (
    SamariumError,
    SamariumIOError,
    SamariumSyntaxError,
    SamariumTypeError,
)

MISSING_ARGS_PATTERN = compile(
    r"\w+\(\) takes exactly one argument \(0 given\)"
    r"|\w+\(\) missing (\d+) required positional argument"
)

NULL_STRING = String()

T = TypeVar("T")

TOO_MANY_ARGS_PATTERN = compile(
    r"\w+\(\) takes (\d+) positional arguments? but (\d+) (?:was|were) given"
)


def dtnow() -> Array:
    utcnow = datetime.utcnow()
    now = datetime.now().timetuple()
    utcnow_tt = utcnow.timetuple()
    tz = now[3] - utcnow_tt[3], now[4] - utcnow_tt[4]
    utcnow_tpl = utcnow_tt[:-3] + (utcnow.microsecond // 1000,) + tz
    return Array(map(Num, utcnow_tpl))


def mkslice(start: Any = None, stop: Any = MISSING, step: Any = None) -> Any:
    if stop is MISSING:
        if start is not None:
            return start
        return Slice(NULL)
    start = NULL if start is None else start
    stop = NULL if stop is None else stop
    step = NULL if step is None else step
    return Slice(start, stop, step)


def print_safe(*args: Attrs | Callable[..., Any] | bool | None) -> Attrs:
    typechecked_args = list(map(correct_type, args))
    return_args = typechecked_args.copy()
    strs = list(map(to_string, typechecked_args))
    types = list(map(type, typechecked_args))
    if tuple in types:
        raise SamariumSyntaxError("missing brackets")
    if GeneratorType in types:
        raise SamariumSyntaxError("invalid comprehension")
    print(*strs)
    if len(return_args) > 1:
        return Array(return_args)
    if not return_args or types[0] is Null:
        return NULL
    return return_args[0]


def readline(prompt: String = NULL_STRING) -> String:
    try:
        return String(input(prompt.val))
    except KeyboardInterrupt:
        msg = "^C"
    except EOFError:
        msg = "^D"
    raise SamariumIOError(msg)


def sleep(*args: Number) -> None:
    if not args:
        raise SamariumTypeError("no argument provided for ,.,")
    if len(args) > 1:
        raise SamariumTypeError(",., only takes one argument")
    if not isinstance((time := args[0]), Number):
        raise SamariumTypeError(",., only accepts integers")
    _sleep(time.val / 1000)


def t(obj: T | None = None) -> T | None:
    return obj


def throw(obj: String | Array = NULL_STRING) -> None:
    note = ""
    if isinstance(obj, Array):
        if len(obj.val) != 2:
            raise SamariumTypeError("array must be of form [error_msg, note]")
        error_msg, note = obj.val
        if not isinstance(error_msg, String):
            raise SamariumTypeError("error message must be a string")
        if not isinstance(note, String):
            raise SamariumTypeError("error note must be a string")
        note = f"\n&1[Note] {note.val}"
    elif isinstance(obj, String):
        error_msg = obj
    else:
        raise SamariumTypeError("throw argument must be a string or a 2-element array")
    raise SamariumError(error_msg.val + note)


def timestamp() -> Number:
    return Num(time_ns() // 1_000_000)
