from django.shortcuts import render
from rest_framework.decorators import renderer_classes
from rest_framework.renderers import JSONRenderer
from Fifa.models import League
from serializers import LeagueSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet

@renderer_classes((JSONRenderer,))
class LeagueViewSet(ReadOnlyModelViewSet):
    queryset = League.objects.all()
    serializer_class = LeagueSerializer
