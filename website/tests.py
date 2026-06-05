from django.test import TestCase
from django.urls import reverse

from .models import FormSubmission


class PageTests(TestCase):
    def test_public_pages_render(self):
        for name in ("home", "about", "visit", "contact", "prayer"):
            with self.subTest(page=name):
                resp = self.client.get(reverse(name))
                self.assertEqual(resp.status_code, 200)

    def test_healthz(self):
        resp = self.client.get("/healthz")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "ok")


class FormTests(TestCase):
    def test_contact_submission_creates_row(self):
        resp = self.client.post(
            reverse("contact"),
            {"name": "Jane", "email": "jane@example.com", "phone": "",
             "message": "Hello, when are services?", "company": "", "source_path": "/contact/"},
        )
        self.assertEqual(resp.status_code, 302)
        sub = FormSubmission.objects.get()
        self.assertEqual(sub.kind, FormSubmission.Kind.CONTACT)
        self.assertEqual(sub.name, "Jane")
        self.assertEqual(sub.source_path, "/contact/")

    def test_prayer_submission_kind(self):
        self.client.post(
            reverse("prayer"),
            {"name": "", "email": "", "phone": "",
             "message": "Please pray for my family.", "company": "", "source_path": "/prayer/"},
        )
        sub = FormSubmission.objects.get()
        self.assertEqual(sub.kind, FormSubmission.Kind.PRAYER)

    def test_message_required(self):
        resp = self.client.post(
            reverse("contact"),
            {"name": "Bob", "email": "", "phone": "", "message": "", "company": ""},
        )
        self.assertEqual(resp.status_code, 200)  # re-rendered with errors
        self.assertEqual(FormSubmission.objects.count(), 0)

    def test_honeypot_blocks_spam(self):
        resp = self.client.post(
            reverse("contact"),
            {"name": "Spammer", "email": "x@y.com", "phone": "",
             "message": "buy stuff", "company": "filled-in"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(FormSubmission.objects.count(), 0)

    def test_source_path_must_be_relative(self):
        self.client.post(
            reverse("contact"),
            {"name": "A", "email": "", "phone": "", "message": "hi",
             "company": "", "source_path": "https://evil.example/x"},
        )
        sub = FormSubmission.objects.get()
        self.assertEqual(sub.source_path, "")
