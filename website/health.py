"""Liveness/readiness endpoint used by the Docker healthcheck and deploy swap."""
from django.db import connection
from django.http import JsonResponse


def healthz(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception as exc:  # pragma: no cover - exercised via container healthcheck
        return JsonResponse({"status": "error", "detail": str(exc)}, status=503)
    return JsonResponse({"status": "ok"})
