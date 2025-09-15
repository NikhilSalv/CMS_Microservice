from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .serializers import RegisterSerializer, ProfileSerializer, FriendshipSerializer, FriendshipDetailSerializer,RespondFriendRequestSerializer, SendOTPSerializer, VerifyOTPSerializer
from .models import Profile, Friendship, OTPVerification
from django.db import models
# Accept or reject a friend request
from rest_framework.views import APIView
from .serializers import UserListSerializer
from rest_framework import status
from django.shortcuts import get_object_or_404 
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta, datetime


import logging
logger = logging.getLogger()

# Send a friendship request
class SendFriendRequestView(generics.CreateAPIView):
    serializer_class = FriendshipSerializer
    permission_classes = [permissions.IsAuthenticated]

# List all friend requests and friendships for the current user
class FriendshipListView(generics.ListAPIView):
    serializer_class = FriendshipDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Friendship.objects.filter(
        (models.Q(requester=user) | models.Q(addressee=user)),
        status="accepted"
    )

class FriendshipDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Restrict queryset so that a user can only delete friendships
        where they are either the requester or the addressee.
        """
        if getattr(self, 'swagger_fake_view', False):
            return Friendship.objects.none()  # empty queryset for docs
        
        
        user = self.request.user
        return Friendship.objects.filter(
        (models.Q(requester=user) | models.Q(addressee=user)),
        status="accepted"
    )

    def delete(self, request, *args, **kwargs):
        friendship = get_object_or_404(self.get_queryset(), pk=kwargs["pk"])
        logger.info(f"The user to be deleted={friendship.__dict__}")
        friendship.delete()
        return Response(
            {"detail": "Friendship removed successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


class RespondFriendRequestView(generics.GenericAPIView):
    serializer_class = RespondFriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    queryset = Friendship.objects.none()

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Friendship.objects.none()
        return Friendship.objects.all()


    def post(self, request, pk):
        user = request.user
        
        try:
            friendship = Friendship.objects.get(id=pk)
        except Friendship.DoesNotExist:
            return Response({"detail": "Friend request not found."}, status=status.HTTP_404_NOT_FOUND)

        # Only the addressee can accept/reject
        if friendship.addressee != user:
            return Response({"detail": "You are not allowed to respond to this request."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action = serializer.validated_data['action']

        # Expect action parameter in request body: 'accept' or 'reject'
        action = request.data.get('action')
        if action not in ['accept', 'reject']:
            return Response({"detail": "Invalid action. Must be 'accept' or 'reject'."}, status=status.HTTP_400_BAD_REQUEST)

        if action == 'accept':
            friendship.status = 'accepted'
            friendship.save()
            return Response({"detail": "Friend request accepted."}, status=status.HTTP_200_OK)
        else:  # reject
            friendship.delete()
            return Response({"detail": "Friend request rejected."}, status=status.HTTP_200_OK)

# Registration endpoint
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

# Profile endpoint (get/update)
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile

class SendOTPView(generics.GenericAPIView):
    serializer_class = SendOTPSerializer
    permission_classes = []  # allow anyone to request OTP

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp = serializer.create_otp()
        expires_at = timezone.now() + timedelta(minutes=5)

        OTPVerification.objects.create(
            email=serializer.validated_data['email'],
            otp=otp,
            expires_at=expires_at
        )

        # send OTP via email
        send_mail(
            'Your OTP Code',
            f'Your OTP is: {otp}',
            'no-reply@yourdomain.com',
            [serializer.validated_data['email']],
        )

        return Response({"detail": "OTP sent to email"}, status=status.HTTP_200_OK)

class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        otp_input = serializer.validated_data['otp']

        try:
            otp_obj = OTPVerification.objects.get(email=email, otp=otp_input, is_verified=False)
        except OTPVerification.DoesNotExist:
            return Response({"detail": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

        if otp_obj.is_expired():
            return Response({"detail": "OTP expired"}, status=status.HTTP_400_BAD_REQUEST)

        # Create the user
        user = User.objects.create_user(
            username=serializer.validated_data['username'],
            email=email,
            password=serializer.validated_data['password']
        )
        Profile.objects.create(user=user, display_name=user.username)

        # Mark OTP as verified
        otp_obj.is_verified = True
        otp_obj.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": {
                "username": user.username,
                "email": user.email
            },
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }, status=status.HTTP_201_CREATED)



# Optional: helper to return JWT after registration
class RegisterAndLoginView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            logger.info("Validation error: %s", serializer.errors)  # <- log it
            raise  # re-raise so DRF still returns 400
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": serializer.data,
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        })
    
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]


class ReceivedFriendRequestsView(APIView):
    permission_classes = [permissions.IsAuthenticated]


    def get(self, request):
        user = request.user
        logger.info(f"request params {request.__dict__}")
        # Filter friendships where the logged-in user is the addressee and status is 'requested'
        received_requests = Friendship.objects.filter(addressee=user, status='requested')
        logger.info(f"the logged in user={user.username}, type={received_requests[0].__dict__}")
        serializer = FriendshipSerializer(received_requests, many=True)
        return Response(serializer.data)
