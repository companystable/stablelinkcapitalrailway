from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from home.views import zoho_oauth_callback

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('userprofile/', include('userprofile.urls')),
    path('investment/', include('investment.urls')),
    path('connectwallet/', include('connectwallet.urls')),

    # Correct
    path('zoho/oauth/callback/', zoho_oauth_callback, name='zoho_oauth_callback'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
