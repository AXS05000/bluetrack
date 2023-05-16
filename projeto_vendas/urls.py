from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# LEMBRE-SE DE TROCAR A ROTA DO ADMIN PARA FICAR MAIS SEGURO
urlpatterns = [
    path('axsadmin/', admin.site.urls),
    path('', include('core.urls')),
    path('', include('usuarios.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
