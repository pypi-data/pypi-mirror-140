from django.db import models


class ExampleModel(models.Model):
    text = models.CharField(max_length=100)
    number = models.IntegerField(default=1)

    class Meta:
        app_label = 'tests'


class ExampleM2MModel(models.Model):
    number = models.IntegerField(default=1)

    class Meta:
        app_label = 'tests'


class NestedM2MModel(models.Model):
    number = models.IntegerField(default=1)

    class Meta:
        app_label = 'tests'


class ExampleNested(models.Model):
    many_to_many = models.ManyToManyField(NestedM2MModel)

    class Meta:
        app_label = 'tests'


class ExampleComplexModel(models.Model):
    text = models.CharField(max_length=100)
    foreign = models.ForeignKey(ExampleModel, on_delete=models.CASCADE)
    nested = models.ForeignKey(ExampleNested, on_delete=models.CASCADE)
    many_to_many = models.ManyToManyField(ExampleM2MModel)

    class Meta:
        app_label = 'tests'
