from django.db import models

from successions.fields import SuccessionField


class Task(models.Model):
    number = SuccessionField(
        max_length=64,
        prefix="TSK-",
        suffix="-%year%",
        padding=5,
    )
