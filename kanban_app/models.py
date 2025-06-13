from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Board(models.Model):
    title = models.CharField(max_length=100)
    members = models.ManyToManyField('auth.User', related_name='boards')
    member_count = models.PositiveIntegerField(default=0)
    ticket_count = models.PositiveIntegerField(default=0)
    tasks_high_prio_count = models.PositiveIntegerField(default=0)
    owner_id = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, related_name='owned_boards'
    )

    def __str__(self):
        return self.title
    
class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='tasks')
    due_date = models.DateField(blank=True, null=True)

    assignee_id = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, related_name='tasks'
    )
    reviewer_id = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, related_name='review_tasks', null=True, blank=True
    )

    status = models.CharField(max_length=20, choices=[
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'Review'),
        ('done', 'Done'),
    ], default='review')

    priority = models.CharField(max_length=10, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], default='medium')    

    def __str__(self):
        return self.title
    
class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author.username} on {self.task.title}'