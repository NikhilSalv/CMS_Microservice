from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserListView
from .views import (
    RegisterAndLoginView, ProfileView,
    SendFriendRequestView, FriendshipListView, RespondFriendRequestView
)

urlpatterns = [
    path('auth/register/', RegisterAndLoginView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profiles/me/', ProfileView.as_view(), name='profile-me'),
     # friendship
    path('friendships/', FriendshipListView.as_view(), name='friendship-list'),
    path('friendships/request/', SendFriendRequestView.as_view(), name='friendship-request'),
    path('friendships/respond/<int:pk>/', RespondFriendRequestView.as_view(), name='friendship-respond'),
    path('users/', UserListView.as_view(), name='user-list'), 
]
