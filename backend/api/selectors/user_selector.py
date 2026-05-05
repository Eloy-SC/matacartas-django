from django.contrib.auth import get_user_model

def get_users_by_username(username):
    UserModel = get_user_model()
    return UserModel.objects.filter(username=username)

def get_users_by_email(email):
    UserModel = get_user_model()
    return UserModel.objects.filter(email=email)