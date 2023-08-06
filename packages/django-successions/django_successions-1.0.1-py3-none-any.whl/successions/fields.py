from django.core import checks
from django.db import models
from successions.exceptions import SuccessionDoesNotMatch

from successions.utils import get_number_from_value, generate_next_value

from .models import Succession

ZERO = 0


class SuccessionField(models.CharField):

    description = "Usefull for generate successions in a field"

    def __init__(self, prefix="", suffix="", padding=1, increment=1, *args, **kwargs):
        kwargs.setdefault("max_length", 64)
        self.prefix = prefix
        self.suffix = suffix
        self.padding = padding
        self.increment = increment
        super().__init__(*args, **kwargs)

    def check(self, **kwargs):
        meta = self.model._meta
        self.succession_name = "{}_{}_{}".format(
            meta.app_label, meta.model_name, self.attname
        )
        self.current = None
        return [
            *super().check(**kwargs),
            *self._check_prefix(),
            *self._check_suffix(),
            *self._check_padding(),
            *self._check_increment(),
        ]

    def _check_prefix(self):
        if not isinstance(self.prefix, str):
            return [checks.Error("'prefix' must be a str instance.", obj=self)]
        return []

    def _check_suffix(self):
        if not isinstance(self.suffix, str):
            return [checks.Error("'suffix' must be a str instance.", obj=self)]

        return []

    def _check_padding(self):
        if not isinstance(self.padding, int) or not self.padding > 0:
            return [checks.Error("'padding' must be a positive integer.", obj=self)]

        return []

    def _check_increment(self):
        if not isinstance(self.increment, int) or not self.increment > 0:
            return [checks.Error("'increment' must be a positive integer.", obj=self)]

        return []

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.prefix:
            kwargs["prefix"] = self.prefix
        if self.suffix:
            kwargs["suffix"] = self.suffix
        if self.padding != 1:
            kwargs["padding"] = self.padding
        if self.increment != 1:
            kwargs["increment"] = self.increment

        return name, path, args, kwargs

    def get_succession_kwargs(self):
        return {
            "prefix": self.prefix,
            "suffix": self.suffix,
            "padding": self.padding,
            "increment": self.increment,
        }

    def check_current_number(self):
        if not self.current:
            defaults = self.get_succession_kwargs()
            succession = Succession.objects.update_or_create(
                name=self.succession_name, defaults=defaults
            )[0]

            self.current = succession.current_value or ZERO

    def update_current_number(self, number):
        self.current = number
        Succession.objects.filter(name=self.succession_name).update(
            current_value=self.current
        )

    def generate_next_value(self):
        return generate_next_value(
            self.current, self.increment, self.padding, self.prefix, self.suffix
        )

    def pre_save(self, model_instance, add):
        value = super().pre_save(model_instance, add)

        if add:
            self.check_current_number()
            if value:
                number = get_number_from_value(value, self.prefix, self.suffix)
                if not number:
                    raise SuccessionDoesNotMatch(value)

                if number > self.current:
                    self.update_current_number(number)
            else:
                next_value, next_number = self.generate_next_value()
                setattr(model_instance, self.attname, next_value)
                self.update_current_number(next_number)

        return value
