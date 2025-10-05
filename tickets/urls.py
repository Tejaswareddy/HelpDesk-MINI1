from django.urls import path
from . import views

urlpatterns = [
    path('tickets', views.TicketListCreateAPIView.as_view()),
    path('tickets/<uuid:pk>', views.TicketDetailAPIView.as_view()),
    path('tickets/<uuid:pk>/comments', views.CommentCreateAPIView.as_view()),
    path('auth/register', views.RegisterAPIView.as_view()),
    path('auth/login', views.LoginAPIView.as_view()),
]
