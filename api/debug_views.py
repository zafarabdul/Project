from django.conf import settings
from django.http import HttpResponse

def debug_paths(request):
    return HttpResponse(f"""
    <html><body>
    <h1>Path Debug Info</h1>
    <p><b>BASE_DIR:</b> {settings.BASE_DIR}</p>
    <p><b>MEDIA_ROOT:</b> {settings.MEDIA_ROOT}</p>
    <p><b>MEDIA_URL:</b> {settings.MEDIA_URL}</p>
    <p><b>STATIC_ROOT:</b> {settings.STATIC_ROOT if hasattr(settings, 'STATIC_ROOT') else 'Not Set'}</p>
    <p><b>STATIC_URL:</b> {settings.STATIC_URL}</p>
    </body></html>
    """)
