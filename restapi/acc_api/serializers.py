import email
from pyexpat import model
from rest_framework import serializers
from login import models


class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    class Meta:
        model = models.CustomUser
        fields = ['email', 'fname', 'sname', 'phone_num', 'password', 'password2']
        extra_kargs = {
            'password': {'write-only': True}
        }

    def save(self):
        account = models.CustomUser(
            phone_num = self.validated_data['phone_num'],
            fname = self.validated_data['fname'],
            sname = self.validated_data['sname'],
            email = self.validated_data['email']
        )
        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords must match'})
        if models.CustomUser.objects.filter(email=email).exists():
            if str(account) != str(email):
                raise serializers.ValidationError({'email': 'Email already exists'})
                    
        account.set_password(password)
        account.save()
        return account
