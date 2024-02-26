import click 
import re
from datetime import date, timedelta

class DayParamType(click.ParamType):
    name="day"
    def convert(self, value, param, ctx):
        if value == "today":
            return date.today()
        if value == "yesterday":
            return date.today() + timedelta(days=-1)
        if value == "tomorrow":
            return date.today() + timedelta(days=+1)
        try:
            return date.fromisoformat(value)    
        except ValueError as e:
            self.fail(f"{value!r} is not a correct date.", param, ctx)

DAY = DayParamType()