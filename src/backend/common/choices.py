from django.db import models


class Domain(models.TextChoices):
    """Subject areas of tasks and terms."""

    IT = "it", "IT"
    MEDICINE = "medicine", "Medicine"
    ENGINEERING = "engineering", "Engineering"
    EVERYDAY = "everyday", "Everyday life"
