from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({
        'status': 'ok',
        'message': 'FoodShare AI API is running.',
        'service': 'foodshare-ai',
        'environment': settings.APP_ENV,
        'timestamp': timezone.now().isoformat(),
        'version': 'v1',
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health_check, name='health-check'),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/donations/', include('apps.donations.urls')),
    path('api/matching/', include('apps.matching.urls')),
    path('api/tracking/', include('apps.tracking.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/feedback/', include('apps.feedback.urls')),
    path('api/fraud-detection/', include('apps.fraud_detection.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
    path('api/ai/', include('apps.ai_engine.urls')),
    path('api/ai-engine/', include('apps.ai_engine.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
