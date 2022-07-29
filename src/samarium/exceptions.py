import sys
from dahlia import dahlia
from re import compile

from .runtime import Runtime


SINGLE_QUOTED_NAME = compile(r"'(\w+)'")


def handle_exception(exception: Exception):
    exc_type = type(exception)
    name = exc_type.__name__
    if exc_type is SyntaxError:
        exception = SamariumSyntaxError(
            f"invalid syntax at {int(str(exception).split()[-1][:-1])}"
        )
    elif exc_type in {AttributeError, NameError}:
        names = SINGLE_QUOTED_NAME.findall(str(exception))
        if names == ["entry"]:
            names = ["no entry function defined"]
        exception = NotDefinedError(".".join(names))
        name = "NotDefinedError"
    elif exc_type not in {AssertionError, NotDefinedError}:
        name = exc_type.__name__
        if name.startswith("Samarium"):
            name = name.removeprefix("Samarium")
        else:
            name = f"External{name}".replace("ExternalZeroDivision", "Math")
    if exc_type is not SamariumError:
        exception.args = (" ".join(i.removeprefix("sm_") for i in exception.args[0].split(" ")),)
    sys.stderr.write(dahlia(f"&4[{name}] {exception}\n"))
    if Runtime.quit_on_error:
        exit(1)


class SamariumError(Exception):
    pass


class NotDefinedError(SamariumError):
    def __init__(self, inp: object, message: str = ""):
        if isinstance(inp, str):
            message = inp
            inp = ""
        else:
            inp = type(inp).__name__
        super().__init__(f"{inp}.{message}" if inp else message)


class SamariumImportError(SamariumError):
    pass


class SamariumSyntaxError(SamariumError):
    pass


class SamariumTypeError(SamariumError):
    pass


class SamariumValueError(SamariumError):
    pass


class SamariumIOError(SamariumError):
    pass
