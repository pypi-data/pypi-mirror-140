import click
from pytimeparse import parse


class TimeDeltaParamType(click.ParamType):
    name = "timedelta"

    def convert(self, value, param, ctx):
        try:
            return parse(value)
        except ValueError:
            self.fail(f"{value!r} is not a valid ISO datetime", param, ctx)


TIME_DELTA = TimeDeltaParamType()
