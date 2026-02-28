import os
import django
import sys

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodsystem.settings')
django.setup()

from django.contrib.auth.models import User

# Check if superuser exists, if not create one
if not User.objects.filter(username='rutuja').exists():
    User.objects.create_superuser('rutuja', 'rutuja@example.com', 'rutuja2027')
    print('Superuser created successfully!')
    print('Username: rutuja')
    print('Password: rutuja2027')
else:
    print('Superuser already exists!')
    print('Username: rutuja')
    print('Password: rutuja2027')
