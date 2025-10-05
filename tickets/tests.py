from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from tickets.models import Ticket, TimelineEntry
from django.utils import timezone
from django.core.cache import cache
import json
import time
import tickets.middleware as mw


class HelpDeskAPITests(TestCase):
    def setUp(self):
        cache.clear()
        # create users
        self.user = User.objects.create_user('user1', password='password')
        self.agent = User.objects.create_user('agent', password='password')
        self.admin = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        # tokens
        self.user_token = Token.objects.create(user=self.user)
        self.agent_token = Token.objects.create(user=self.agent)

    def auth_headers(self, token):
        return {'HTTP_AUTHORIZATION': f'Token {token.key}'}

    def test_health(self):
        resp = self.client.get('/api/health')
        self.assertEqual(resp.status_code, 200)

    def test_ticket_creation_and_sla_and_timeline(self):
        # create ticket
        data = {'title': 'SLA test', 'description': 'desc', 'sla_minutes': 30}
        resp = self.client.post('/api/tickets', data=json.dumps(data), content_type='application/json', **self.auth_headers(self.user_token))
        self.assertEqual(resp.status_code, 201)
        body = resp.json()
        tid = body['id']
        t = Ticket.objects.get(id=tid)
        # SLA deadline set approx 30 minutes ahead
        delta = t.sla_deadline - timezone.now()
        self.assertTrue(delta.total_seconds() > 25*60)
        # timeline entry created
        self.assertTrue(TimelineEntry.objects.filter(ticket=t, action='created').exists())

    def test_breached_listing(self):
        # create a breached ticket (deadline in past)
        t = Ticket.objects.create(title='old', description='old', creator=self.user, sla_minutes=1)
        t.sla_deadline = timezone.now() - timezone.timedelta(minutes=10)
        t.save()
        resp = self.client.get('/api/tickets?breached=true')
        self.assertEqual(resp.status_code, 200)
        items = resp.json()['items']
        ids = [it['id'] for it in items]
        self.assertIn(str(t.id), ids)

    def test_pagination(self):
        # create 12 tickets
        for i in range(12):
            Ticket.objects.create(title=f't{i}', description='d', creator=self.user)
        resp = self.client.get('/api/tickets?limit=5&offset=0')
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(len(body['items']), 5)
        self.assertEqual(body['next_offset'], 5)

        resp2 = self.client.get('/api/tickets?limit=5&offset=5')
        self.assertEqual(len(resp2.json()['items']), 5)

    def test_optimistic_locking_conflict(self):
        t = Ticket.objects.create(title='lock', description='d', creator=self.user)
        # simulate client read
        client_version = t.version
        # another update increments version
        t.status = 'in_progress'
        t.version += 1
        t.save()
        # now client attempts patch with stale version
        patch = {'version': client_version, 'status': 'resolved'}
        resp = self.client.patch(f'/api/tickets/{t.id}', data=json.dumps(patch), content_type='application/json', **self.auth_headers(self.agent_token))
        self.assertEqual(resp.status_code, 409)

    def test_idempotency_on_ticket_create(self):
        key = 'idem-test-1'
        data = {'title': 'idem', 'description': 'dup', 'sla_minutes': 10}
        h = {'HTTP_IDEMPOTENCY_KEY': key, 'HTTP_AUTHORIZATION': f'Token {self.user_token.key}'}
        r1 = self.client.post('/api/tickets', data=json.dumps(data), content_type='application/json', **h)
        self.assertEqual(r1.status_code, 201)
        count_after_first = Ticket.objects.filter(title='idem').count()
        r2 = self.client.post('/api/tickets', data=json.dumps(data), content_type='application/json', **h)
        # second should return cached response (200) and not create a duplicate
        self.assertIn(r2.status_code, (200,201))
        count_after_second = Ticket.objects.filter(title='idem').count()
        self.assertEqual(count_after_first, count_after_second)

    def test_rate_limit_enforced(self):
        # lower rate limit to 5 for faster testing
        orig = mw.RATE_LIMIT
        mw.RATE_LIMIT = 5
        cache.clear()
        # send 6 quick requests
        headers = {'HTTP_AUTHORIZATION': f'Token {self.user_token.key}'}
        last_status = None
        for i in range(6):
            r = self.client.get('/api/health', **headers)
            last_status = r.status_code
        # we expect last to be 429
        self.assertEqual(last_status, 429)
        # restore
        mw.RATE_LIMIT = orig
