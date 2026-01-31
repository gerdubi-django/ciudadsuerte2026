from django.db import models


class Person(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    id_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, default="")
    phone = models.CharField(max_length=20)
    birth_date = models.DateField()

    class Meta:
        ordering = ("last_name", "first_name")

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} ({self.id_number})"
