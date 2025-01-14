from rest_framework import serializers
from .models import User, Charger, ChargingSession

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class ChargerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Charger
        fields = '__all__'
        
class ChargingSessionSerializer(serializers.ModelSerializer):
    client_address = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    charger_address = serializers.PrimaryKeyRelatedField(queryset=Charger.objects.all())
    charger_owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    total_cost = serializers.IntegerField(required=False)
    is_completed = serializers.BooleanField(required=False)
    date = serializers.DateTimeField(required=False)
    demand = serializers.IntegerField()

    class Meta:
        model = ChargingSession
        fields = '__all__'
