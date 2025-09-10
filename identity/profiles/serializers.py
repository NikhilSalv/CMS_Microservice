from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Friendship
from django.contrib.auth.password_validation import validate_password
import random

import logging
logger = logging.getLogger(__name__)

# User registration serializer
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)  # confirmation

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        # create empty profile automatically
        Profile.objects.create(user=user, display_name=user.username)
        return user


# this serialiser is removed because, in this logic, the user model was getting created before the OTP verification.
# this created an issue of populating the data with inactive users. 

# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
#     password2 = serializers.CharField(write_only=True, required=True)

#     class Meta:
#         model = User
#         fields = ('username', 'email', 'password', 'password2')

#     def validate(self, attrs):
#         if attrs['password'] != attrs['password2']:
#             raise serializers.ValidationError({"password": "Password fields didn't match."})
#         return attrs

#     def create(self, validated_data):
#         user = User.objects.create(
#             username=validated_data['username'],
#             email=validated_data['email']
#         )
#         user.set_password(validated_data['password'])
#         user.is_active = False  # deactivate until OTP verified
#         user.save()
#         Profile.objects.create(user=user, display_name=user.username)
#         return user


class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
    
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value

    def create_otp(self):
        otp = f"{random.randint(100000, 999999)}"
        return otp

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

# Profile serializer
class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Profile
        fields = ('username', 'email', 'display_name', 'avatar_url', 'bio')


class FriendshipSerializer(serializers.ModelSerializer):
    # action = serializers.ChoiceField(choices=['accept', 'reject'])
    requester = serializers.ReadOnlyField(source='requester.username')
    addressee = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())

    class Meta:
        model = Friendship
        fields = ('id', 'requester', 'addressee', 'status', 'created_at')
        read_only_fields = ('status', 'created_at')

    def create(self, validated_data):
        # set requester as current user
        user = self.context['request'].user
        validated_data['requester'] = user
        validated_data['status'] = 'requested'

        addressee = validated_data['addressee']
        logger.info(f"Creating friendship: requester={user.username}, addressee={addressee.username}")

        return super().create(validated_data)

# Serializer to view friendships
class FriendshipDetailSerializer(serializers.ModelSerializer):
    requester = serializers.CharField(source='requester.username', read_only=True)
    addressee = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())

    class Meta:
        model = Friendship
        fields = ('id', 'requester', 'addressee', 'status', 'created_at')


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email")

class RespondFriendRequestSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['accept', 'reject'])