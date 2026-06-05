import uuid

from django.db import models


class FormSubmission(models.Model):
    """
    A public contact or prayer submission.

    Mirrors the proven shape of online-sermon's feedback_cards
    (connection -> contact, prayer), minus the multi-tenant columns:
    message is required; name/email/phone are optional; source_path
    records the page the form was submitted from; reviewed_at drives
    the admin review inbox.
    """

    class Kind(models.TextChoices):
        CONTACT = "contact", "Contact"
        PRAYER = "prayer", "Prayer"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kind = models.CharField(max_length=20, choices=Kind.choices)
    message = models.TextField(max_length=4000)
    name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    source_path = models.CharField(max_length=2000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["kind", "-created_at"]),
            models.Index(
                fields=["-created_at"],
                name="unreviewed_idx",
                condition=models.Q(reviewed_at__isnull=True),
            ),
        ]

    def __str__(self):
        who = self.name or self.email or "anonymous"
        return f"{self.get_kind_display()} from {who} ({self.created_at:%Y-%m-%d})"

    @property
    def is_reviewed(self) -> bool:
        return self.reviewed_at is not None
