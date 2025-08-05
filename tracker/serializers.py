from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Project, Bug, Comment, ActivityLog

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        
        

class ProjectSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    bugs_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'owner', 'bugs_count', 'created_at', 'updated_at']
    
    def get_bugs_count(self, obj):
        return obj.bugs.count()
    
    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)
    
    


class BugSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Bug
        fields = [
            'id', 'title', 'description', 'status', 'priority', 
            'assigned_to', 'assigned_to_id', 'project', 'project_name',
            'created_by', 'comments_count', 'created_at', 'updated_at'
        ]
    
    def get_comments_count(self, obj):
        return obj.comments.count()
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
    
    
    
    
class CommentSerializer(serializers.ModelSerializer):
    commenter = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'bug', 'commenter', 'message', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['commenter'] = self.context['request'].user
        return super().create(validated_data)
    


class ActivityLogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ActivityLog
        fields = ['id', 'project', 'user', 'action', 'entity_type', 'entity_id', 'details', 'created_at']

    
    