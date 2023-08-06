from datetime import datetime

from django.db import models
from django.test import TestCase

from successions.fields import SuccessionField


class TaskWithSuccessionField(models.Model):
    number = SuccessionField(max_length=64, prefix="TSK-", suffix="-%year%", padding=5)

    class Meta:
        app_label = "testapp"


class Test(TestCase):
    def setUp(self):
        self.model = TaskWithSuccessionField()
        self.next_value = "TSK-00001-{}".format(datetime.now().year)

    def test_succession_field(self):
        field = self.model._meta.get_field("number")
        kwargs = field.get_succession_kwargs(self.model)
        next_value = field.generate_next_value(**kwargs)[0]
        self.assertEqual(next_value, self.next_value)

    def test_save_with_succesion_field(self):
        self.assertEqual(self.model.number, "")
        self.model.save()
        self.assertEqual(self.model.number, self.next_value)
