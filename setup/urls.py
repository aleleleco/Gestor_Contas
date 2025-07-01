
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import os

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.gestor_contas.urls')),  # Use o caminho completo
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Servir arquivos externos
    urlpatterns += [
        path('externos/<path:path>', serve, {
            'document_root': 'C:/Users/PC-Leleco/Dropbox/Pessoal/ContasPagas',
        }),
    ]