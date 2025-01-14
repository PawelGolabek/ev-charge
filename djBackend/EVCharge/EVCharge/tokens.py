from rest_framework_simplejwt.tokens import RefreshToken

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    refresh['role'] = user.role.name
    refresh['user_address'] = user.user_address
    refresh['nonce'] = user.nonce
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
