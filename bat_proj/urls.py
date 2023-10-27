from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static



handler404 = 'bat_app.views.error_404'  
handler500 = 'bat_app.views.error_500'  

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('bat_app.urls'))
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)