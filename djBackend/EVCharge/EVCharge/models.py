from django.db import models

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'role'

class User(models.Model):
    user_address = models.CharField(max_length=42)  # Assuming Ethereum-like addresses
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    balance = models.IntegerField()
    contribution = models.PositiveIntegerField()

    class Meta:
        db_table = 'user'

class Charger(models.Model):
    charger_address = models.CharField(max_length=42)
    price_per_kwh = models.IntegerField()
    owner = models.CharField(max_length=42)

    class Meta:
        db_table = 'charger'


class ChargingSession(models.Model):
    client_address = models.TextField()
    charger_address = models.TextField()
    total_cost = models.IntegerField()
    demand = models.IntegerField()
    is_completed = models.BooleanField()
    charger_owner = models.TextField()

    class Meta:
        db_table = 'charging_session'
