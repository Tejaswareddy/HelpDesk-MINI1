from rest_framework import serializers
from .models import Ticket, Comment, TimelineEntry, Profile
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username','email')

class TicketSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    assignee = UserSerializer(read_only=True)
    class Meta:
        model = Ticket
        fields = '__all__'

class TicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ('title','description','sla_minutes')

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = '__all__'

class TimelineSerializer(serializers.ModelSerializer):
    actor = UserSerializer(read_only=True)
    class Meta:
        model = TimelineEntry
        fields = '__all__'

# move ticket serializer after comment/timeline

class TicketSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    assignee = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    timeline = TimelineSerializer(many=True, read_only=True)
    class Meta:
        model = Ticket
        fields = '__all__'
