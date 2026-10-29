from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        PARTICIPANT = "participant", "Participant"
        REVIEWER = "reviewer", "Reviewer"
        MODERATOR = "moderator", "Moderator"
        ADMIN = "admin", "Administrator"

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PARTICIPANT)
    # Public identifier for attribution; email is never shown publicly (NFR-04).
    display_name = models.CharField(max_length=60, blank=True)

    REVIEWER_ROLES = {Role.REVIEWER, Role.MODERATOR, Role.ADMIN}
    MODERATOR_ROLES = {Role.MODERATOR, Role.ADMIN}

    @property
    def is_reviewer(self):
        return self.role in self.REVIEWER_ROLES

    @property
    def is_moderator(self):
        return self.role in self.MODERATOR_ROLES

    @property
    def public_name(self):
        return self.display_name or self.username
