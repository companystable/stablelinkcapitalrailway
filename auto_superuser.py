from django.contrib.auth import get_user_model
from django.db import OperationalError
User = get_user_model()
username = "shapirofc"
password = "shapirofcsite$"
email = ""
try:
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
        print("Superuser created ✔")
    else:
        print("Superuser already exists ✔")
except OperationalError:
    print("Database not ready")
