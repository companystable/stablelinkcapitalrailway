
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from home.views import zoho_oauth_callback


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),  # Include the seedview app's URLs
    path('userprofile/', include('userprofile.urls')),
    path('investment/', include('investment.urls')),  # Ensure 'investment.urls' is correct
    path('connectwallet/', include('connectwallet.urls')),
    path('zoho/oauth/callback/', home_views.zoho_oauth_callback, name='zoho_oauth_callback'),
]

# Add this at the end to serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

