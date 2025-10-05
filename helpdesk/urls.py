from django.urls import path, include
from django.http import JsonResponse
from django.views.static import serve
from django.conf import settings
from django.views.generic import TemplateView

def health(request):
    return JsonResponse({'status': 'ok'})

def meta(request):
    return JsonResponse({'name': 'HelpDesk Mini', 'version': '0.1'})

urlpatterns = [
    path('api/health', health),
    path('api/_meta', meta),
    path('api/', include('tickets.urls')),
    path('.well-known/hackathon.json', lambda r: serve(r, path='hackathon.json', document_root=str(settings.BASE_DIR / '.well-known'))),
    path('', TemplateView.as_view(template_name='index.html')),
]
