from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Project, Bug, Comment, ActivityLog
from .serializers import ProjectSerializer, BugSerializer, CommentSerializer, ActivityLogSerializer
from .permissions import IsOwnerOrReadOnly, IsProjectMemberOrReadOnly



# Create your views here.

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    
    def get_queryset(self):
        return Project.objects.filter(
            Q(owner=self.request.user) | Q(bugs__assigned_to=self.request.user)
        ).distinct()
        
        
        
        

class BugViewSet(viewsets.ModelViewSet):
    serializer_class = BugSerializer
    permission_classes = [IsAuthenticated, IsProjectMemberOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'project', 'assigned_to']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'priority']
    
    def get_queryset(self):
        return Bug.objects.filter(
            Q(project__owner=self.request.user) | 
            Q(assigned_to=self.request.user) | 
            Q(created_by=self.request.user)
        ).distinct()
        
    
    
    @action(detail=False, methods=['get'])
    def assigned_to_me(self, request):
        """Get bugs assigned to current user"""
        bugs = self.get_queryset().filter(assigned_to=request.user)
        serializer = self.get_serializer(bugs, many=True)
        return Response(serializer.data)
    
    
    def perform_create(self, serializer):
        bug = serializer.save()
        self._send_websocket_notification('bug_created', bug)
        self._log_activity(bug, 'created', 'bug')
        
        
    
    def perform_update(self, serializer):
        old_status = self.get_object().status
        bug = serializer.save()
        
        # Send notification if status changed
        if old_status != bug.status:
            self._send_websocket_notification('bug_status_changed', bug, {
                'old_status': old_status,
                'new_status': bug.status
            })
        else:
            self._send_websocket_notification('bug_updated', bug)
        
        self._log_activity(bug, 'updated', 'bug')
        
        
    
    def _send_websocket_notification(self, event_type, bug, extra_data=None):
        """Send WebSocket notification to project room"""
        channel_layer = get_channel_layer()
        data = {
            'type': 'bug_notification',
            'event_type': event_type,
            'bug': BugSerializer(bug).data,
            'user': bug.created_by.username if event_type == 'bug_created' else self.request.user.username,
        }
        if extra_data:
            data.update(extra_data)
        
        async_to_sync(channel_layer.group_send)(
            f"project_{bug.project.id}",
            data

        )
        
        
    
    def _log_activity(self, bug, action, entity_type):
        """Log activity for the bug"""
        ActivityLog.objects.create(
            project=bug.project,
            user=self.request.user,
            action=action,
            entity_type=entity_type,
            entity_id=bug.id,
            details={
                'title': bug.title,
                'status': bug.status,
                'priority': bug.priority,
            }
        )



class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['bug']
    
    
    def get_queryset(self):
        return Comment.objects.filter(
            Q(bug__project__owner=self.request.user) | 
            Q(bug__assigned_to=self.request.user) | 
            Q(bug__created_by=self.request.user) |
            Q(commenter=self.request.user)
        ).distinct()
        
        
    
    def perform_create(self, serializer):
        comment = serializer.save()
        self._send_comment_notification(comment)
        self._log_activity(comment)
        
        
    
    def _send_comment_notification(self, comment):
        """Send WebSocket notification for new comment"""
        channel_layer = get_channel_layer()
        
        # Notify project room
        async_to_sync(channel_layer.group_send)(
            f"project_{comment.bug.project.id}",
            {
                'type': 'comment_notification',
                'comment': CommentSerializer(comment).data,
                'bug': BugSerializer(comment.bug).data,
                'user': comment.commenter.username,
            }
        )
        
        
        
        # Send personal notifications to bug creator and assigned user
        recipients = [comment.bug.created_by, comment.bug.assigned_to]
        recipients = [user for user in recipients if user and user != comment.commenter]
        
        for user in recipients:
            async_to_sync(channel_layer.group_send)(
                f"user_{user.id}",
                {
                    'type': 'personal_notification',
                    'notification_type': 'new_comment',
                    'comment': CommentSerializer(comment).data,
                    'bug': BugSerializer(comment.bug).data,
                    'commenter': comment.commenter.username,
                }
            )
            
            
            
            
    def _log_activity(self, comment):
        """Log activity for the comment"""
        ActivityLog.objects.create(
            project=comment.bug.project,
            user=comment.commenter,
            action='commented',
            entity_type='comment',
            entity_id=comment.id,
            details={
                'bug_title': comment.bug.title,
                'message_preview': comment.message[:50] + '...' if len(comment.message) > 50 else comment.message,
            }
        )
        
        
        
        
class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['project', 'action', 'entity_type']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return ActivityLog.objects.filter(
            Q(project__owner=self.request.user) | 
            Q(project__bugs__assigned_to=self.request.user)
        ).distinct()        
        
        
        