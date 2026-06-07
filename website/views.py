import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import ContactForm, PrayerForm

logger = logging.getLogger(__name__)


def home(request):
    return render(request, "website/home.html")


def about(request):
    return render(request, "website/about.html")


def visit(request):
    return render(request, "website/visit.html")


def message(request):
    return render(request, "website/message.html")


def _notify_church(submission):
    """Best-effort email to the church inbox. No-op if unconfigured."""
    if not settings.CHURCH_NOTIFY_EMAIL:
        return
    label = submission.get_kind_display()
    lines = [
        f"New {label.lower()} submission from the website.",
        "",
        f"Name:    {submission.name or '-'}",
        f"Email:   {submission.email or '-'}",
        f"Phone:   {submission.phone or '-'}",
        f"Page:    {submission.source_path or '-'}",
        "",
        "Message:",
        submission.message,
    ]
    try:
        send_mail(
            subject=f"[West Street Baptist] New {label}",
            message="\n".join(lines),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CHURCH_NOTIFY_EMAIL],
            fail_silently=True,
        )
    except Exception:  # pragma: no cover - never block the user on email
        logger.exception("Failed to send %s notification email", label)


def _handle_form(request, *, form_class, template, page_title, done_message):
    source_path = request.POST.get("source_path") or request.get_full_path()
    if request.method == "POST":
        form = form_class(request.POST, source_path=source_path)
        if form.is_valid():
            submission = form.save()
            _notify_church(submission)
            messages.success(request, done_message)
            return redirect(f"{request.path}?sent=1")
        # Honeypot or invalid: fall through and re-render with errors.
    else:
        form = form_class(source_path=source_path)

    return render(
        request,
        template,
        {
            "form": form,
            "page_title": page_title,
            "sent": request.GET.get("sent") == "1",
            "source_path": source_path,
        },
    )


def contact(request):
    return _handle_form(
        request,
        form_class=ContactForm,
        template="website/contact.html",
        page_title="Contact Us",
        done_message="Thank you! We received your message and will be in touch.",
    )


def prayer(request):
    return _handle_form(
        request,
        form_class=PrayerForm,
        template="website/prayer.html",
        page_title="Prayer Request",
        done_message="Received. Thank you for sharing. Our team will be praying.",
    )
