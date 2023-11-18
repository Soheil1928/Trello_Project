from rest_framework import serializers
from .models import Profile, Project, Task, Board, ProjectMembership
from django.contrib.auth.models import User



class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'profile_name', 'bio', 'image_profile']
    

class UserSerializer(serializers.ModelSerializer):
    user_profile = ProfileSerializer(read_only=True)
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'password2', 'first_name', 'last_name', 'user_profile']
        extra_kwargs = {'password': {'write_only': True}}

    def save(self, **kwargs):
        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({'Error': 'Password Dose Not Match'})
        else:
            account = User(username=self.validated_data['username'])
            account.set_password(password)
            account.save()


class ProjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    owner = ProfileSerializer(read_only=True)
    members = serializers.SerializerMethodField()

    def get_members(self, obj):
        queryset = ProjectMembership.objects.filter(project=obj)
        return ProjectMembershipSerializer(queryset, many=True).data

    class Meta:
        model = Project
        fields = ['id','owner','title','description','members']
        read_only_fields = ['owner']


class ProjectMembershipSerializer(serializers.ModelSerializer):
    access_level = serializers.SerializerMethodField()
    class Meta:
        model = ProjectMembership
        fields = ['id', 'project', 'member', 'access_level','created_at']
        
    def get_access_level(self, obj):
        return obj.get_access_level_display()
    
    
class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'