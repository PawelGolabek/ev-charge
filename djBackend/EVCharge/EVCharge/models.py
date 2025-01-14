from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class Role(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'role'


class UserManager(BaseUserManager):
    def create_user(self, user_address, role, password=None):
        if not user_address:
            raise ValueError("Users must have an address")
        user = self.model(user_address=user_address, role=role)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    user_address = models.CharField(max_length=42, unique=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    balance = models.IntegerField()
    contribution = models.PositiveIntegerField()
    last_login = models.DateTimeField(default=now)
    password = models.CharField(max_length=255)
    nonce = models.IntegerField(default=0)

    objects = UserManager()

    USERNAME_FIELD = 'user_address'
    REQUIRED_FIELDS = ['role']

    class Meta:
        db_table = 'user'


class ServerNonce(models.Model):
    nonce = models.IntegerField(default=0)

    class Meta:
        db_table = 'nounce'


class Charger(models.Model):
    charger_address = models.CharField(max_length=42, unique=True)
    price_per_kwh = models.IntegerField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, to_field='user_address', related_name='chargers')

    class Meta:
        db_table = 'charger'


class ChargingSession(models.Model):
    client_address = models.ForeignKey(User, related_name='charging_sessions', on_delete=models.CASCADE)
    charger_address = models.ForeignKey(Charger, on_delete=models.CASCADE)
    total_cost = models.IntegerField()
    demand = models.IntegerField()
    is_completed = models.BooleanField()
    charger_owner = models.ForeignKey(User, related_name='charger_sessions', on_delete=models.CASCADE)
    date = models.DateTimeField(default=now)

    class Meta:
        db_table = 'charging_session'


class TransactionSummary(models.Model):
    seller = models.ForeignKey(User, related_name="transaction_user_address", on_delete=models.CASCADE)
    charger = models.ForeignKey(Charger, related_name="transaction_summaries", on_delete=models.CASCADE)
    total_demand = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount_owed = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    paid =  models.BooleanField(default=False)

    class Meta:
        db_table = 'transaction_summary'

