import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','helpdesk.settings')
django.setup()
from django.contrib.auth.models import User
from tickets.models import Profile, Ticket

if not User.objects.filter(username='admin').exists():
    u = User.objects.create_superuser('admin','admin@example.com','password')
    Profile.objects.create(user=u, role='admin')
if not User.objects.filter(username='agent').exists():
    a = User.objects.create_user('agent', password='password')
    Profile.objects.create(user=a, role='agent')
if not User.objects.filter(username='user1').exists():
    u2 = User.objects.create_user('user1', password='password')
    Profile.objects.create(user=u2, role='user')

if Ticket.objects.count() == 0:
    Ticket.objects.create(title='Test ticket', description='This is a seed ticket', creator=User.objects.get(username='user1'))

print('Seed complete')
