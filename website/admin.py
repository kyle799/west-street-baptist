from django.contrib import admin
from django.utils import timezone

from .models import FormSubmission


@admin.register(FormSubmission)
class FormSubmissionAdmin(admin.ModelAdmin):
    """Review inbox for contact + prayer submissions."""

    list_display = ("created_at", "kind", "name", "email", "phone", "reviewed_badge")
    list_filter = ("kind", "reviewed_at", "created_at")
    search_fields = ("name", "email", "phone", "message")
    date_hierarchy = "created_at"
    readonly_fields = (
        "id",
        "kind",
        "name",
        "email",
        "phone",
        "message",
        "source_path",
        "created_at",
    )
    fields = (
        "kind",
        "name",
        "email",
        "phone",
        "message",
        "source_path",
        "created_at",
        "reviewed_at",
    )
    actions = ("mark_reviewed", "mark_unreviewed")

    @admin.display(description="Reviewed", boolean=True)
    def reviewed_badge(self, obj):
        return obj.is_reviewed

    @admin.action(description="Mark selected as reviewed")
    def mark_reviewed(self, request, queryset):
        updated = queryset.filter(reviewed_at__isnull=True).update(
            reviewed_at=timezone.now()
        )
        self.message_user(request, f"{updated} marked reviewed.")

    @admin.action(description="Mark selected as not reviewed")
    def mark_unreviewed(self, request, queryset):
        updated = queryset.update(reviewed_at=None)
        self.message_user(request, f"{updated} marked not reviewed.")

    def has_add_permission(self, request):
        # Submissions only arrive from the public forms.
        return False
