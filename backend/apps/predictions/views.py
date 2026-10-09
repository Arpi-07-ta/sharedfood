from rest_framework import viewsets

from .models import PredictionResult
from .serializers import PredictionResultSerializer


class PredictionResultViewSet(viewsets.ModelViewSet):
    queryset = PredictionResult.objects.all()
    serializer_class = PredictionResultSerializer
