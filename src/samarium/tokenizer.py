from __future__ import annotations

import re
from typing import Union, cast

from crossandra import Crossandra, CrossandraError, Rule, common

from .exceptions import SamariumSyntaxError, handle_exception
from .tokens import Token


def to_int(string: str) -> int:
    return int(string.replace("/", "1").replace("\\", "0"), 2)


Tokenlike = Union[Token, str, int]

crossandra = Crossandra(
    Token,
    ignore_whitespace=True,
    ignored_characters="`",
    rules=[
        Rule(r"(?:\\|/)+", to_int),
        Rule(r"\w+"),
        common.DOUBLE_QUOTED_STRING,
        Rule(r"==[^\n]*", lambda _: None),
        Rule(r"==<.*>==", lambda _: None, re.M | re.S),
    ]
)


def tokenize(code: str) -> list[Tokenlike]:
    try:
        return cast(list[Tokenlike], crossandra.tokenize(code))
    except CrossandraError as e:
        handle_exception(SamariumSyntaxError(str(e)))
        exit()
