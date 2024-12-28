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
    total_cost = serializers.IntegerField(required=False)
    is_completed = serializers.BooleanField(required=False)
    charger_owner = serializers.CharField(required=False)

    class Meta:
        model = ChargingSession
        fields = '__all__'
