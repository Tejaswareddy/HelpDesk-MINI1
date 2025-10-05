from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Ticket, Comment, TimelineEntry, Profile
from .serializers import TicketSerializer, TicketCreateSerializer, CommentSerializer, TimelineSerializer, UserSerializer
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404

class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        role = request.data.get('role','user')
        if not username or not password:
            return Response({'error': {'code':'FIELD_REQUIRED','field':'username','message':'username required'}}, status=400)
        user = User.objects.create_user(username=username, password=password)
        Profile.objects.create(user=user, role=role)
        token = Token.objects.create(user=user)
        return Response({'token': token.key, 'user': UserSerializer(user).data})

class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = get_object_or_404(User, username=username)
        if not user.check_password(password):
            return Response({'error': {'code':'INVALID_CREDENTIALS'}}, status=400)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserSerializer(user).data})

def paginate_queryset(qs, limit, offset):
    limit = int(limit or 10)
    offset = int(offset or 0)
    items = qs[offset:offset+limit]
    next_offset = offset + len(items)
    return items, next_offset

class TicketListCreateAPIView(APIView):
    def get(self, request):
        q = request.GET.get('q')
        breached = request.GET.get('breached')
        tickets = Ticket.objects.all().order_by('-created_at')
        if breached == 'true':
            now = timezone.now()
            tickets = tickets.filter(sla_deadline__lt=now)
        if q:
            tickets = tickets.filter(Q(title__icontains=q)|Q(description__icontains=q)|Q(comments__body__icontains=q)).distinct()
        limit = request.GET.get('limit')
        offset = request.GET.get('offset')
        items, next_offset = paginate_queryset(list(tickets), limit, offset)
        ser = TicketSerializer(items, many=True)
        return Response({'items': ser.data, 'next_offset': next_offset})

    def post(self, request):
        serializer = TicketCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': {'code':'FIELD_REQUIRED','message':'validation failed'}}, status=400)
        ticket = serializer.save(creator=request.user)
        # set SLA deadline
        ticket.sla_deadline = timezone.now() + timezone.timedelta(minutes=ticket.sla_minutes)
        ticket.save()
        TimelineEntry.objects.create(ticket=ticket, actor=request.user, action='created')
        return Response(TicketSerializer(ticket).data, status=201)

class TicketDetailAPIView(APIView):
    def get(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk)
        return Response(TicketSerializer(ticket).data)

    def patch(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk)
        # optimistic locking
        client_version = int(request.data.get('version', 0))
        if client_version != ticket.version:
            return Response({'error': {'code':'VERSION_MISMATCH'}}, status=409)
        # apply changes
        assignee_id = request.data.get('assignee_id')
        status_val = request.data.get('status')
        if assignee_id:
            ticket.assignee = User.objects.get(id=assignee_id)
        if status_val:
            ticket.status = status_val
        ticket.version += 1
        ticket.save()
        TimelineEntry.objects.create(ticket=ticket, actor=request.user, action='updated', data=request.data)
        return Response(TicketSerializer(ticket).data)

class CommentCreateAPIView(APIView):
    def post(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk)
        body = request.data.get('body')
        parent = request.data.get('parent')
        if not body:
            return Response({'error': {'code':'FIELD_REQUIRED','field':'body','message':'body required'}}, status=400)
        comment = Comment.objects.create(ticket=ticket, author=request.user, body=body, parent_id=parent)
        TimelineEntry.objects.create(ticket=ticket, actor=request.user, action='commented', data={'comment_id': str(comment.id)})
        return Response(CommentSerializer(comment).data, status=201)
