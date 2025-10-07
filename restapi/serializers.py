
from rest_framework import serializers
from restapi import models
from login.models import CustomUser

class DataSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'title',
            'desc',
        )
        model = models.Infor


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
            'phone_num',
        )
        model = CustomUser
        

class ActivaSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'uid',
            'fname',
            'sname',
            'token',
            'acc_token',
            'site_id',
            'phone_num',
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
             

class DrvSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'id',
            'eid',
            'fname',
            'sname',
            'token',
            'act_code',
            'status',
            'hire_date',
            'initia',
            'phone_num',
            'u_pic',
        )



class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'mid',
            'isTyping',
            'message',
            'conv_id',
            'lastOnline',
            'messStat',
            'messType',
            'rec_status',
            'snd_status',
            'rec_usr',
            'snd_usr',
            'sent_date',
        )
        model = models.ChatList



class ChangePasswordSerializer(serializers.Serializer):
    model = CustomUser
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True) 