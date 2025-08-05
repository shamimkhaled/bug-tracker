from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class TimeStampedModel(models.Model):
    """Abstract base model with timestamp fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class Project(TimeStampedModel):
    name = models.CharField(max_length=255)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_projects')
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']

class Bug(TimeStampedModel):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
    ]
    
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Critical', 'Critical'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_bugs')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='bugs')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_bugs')
    
    def __str__(self):
        return f"{self.title} - {self.status}"
    
    class Meta:
        ordering = ['-created_at']

class Comment(TimeStampedModel):
    bug = models.ForeignKey(Bug, on_delete=models.CASCADE, related_name='comments')
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    message = models.TextField()
    
    def __str__(self):
        return f"Comment by {self.commenter.username} on {self.bug.title}"
    
    class Meta:
        ordering = ['created_at']




class ActivityLog(TimeStampedModel):
    """Bonus: Activity Log model"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)  # 'created', 'updated', 'commented', etc.
    entity_type = models.CharField(max_length=20)  # 'bug', 'comment', 'project'
    entity_id = models.PositiveIntegerField()
    details = models.JSONField(default=dict)
    
    def __str__(self):
        return f"{self.user.username} {self.action} {self.entity_type} in {self.project.name}"
    
    class Meta:
        ordering = ['-created_at']


