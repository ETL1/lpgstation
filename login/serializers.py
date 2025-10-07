from rest_framework import serializers
# from restapi import models
from login.models import CustomUser

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'uid',
            'fname',
            'sname',
            'email',
            'phone_num',
        )
        model = CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'uid',
            'fname',
            'sname',
            'token',
            'acc_token',
            'site_id',
        )
        model = CustomUser
        

class ActivaSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'uid',
            'fname',
            'sname',
            'token',
            'acc_token',
            'phone_num',
            'u_pic',
            'site_id',
        )
        model = CustomUser
            

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'uid',
            'fname',
            'sname',
            'email',
            'phone_num',
        )
        model = CustomUser
        
class UserDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'is_active',
        )
        model = CustomUser
             

class ChangePasswordSerializer(serializers.Serializer):
    model = CustomUser
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True) 