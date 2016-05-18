from Fifa.models import League
from rest_framework.serializers import ModelSerializer

class LeagueSerializer(ModelSerializer):
    class Meta:
        model = League