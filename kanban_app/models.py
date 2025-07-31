from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Board(models.Model):
    title = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='boards')
    owner_id = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='owned_boards'
    )

    def __str__(self):
        return self.title


class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='tasks_created')
    board = models.ForeignKey(
        Board, on_delete=models.CASCADE, related_name='tasks')
    due_date = models.DateField(blank=True, null=True)

    assignee = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='tasks_assigned', null=True, blank=True
    )
    reviewer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='tasks_reviewing', null=True, blank=True
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
        return f'Task "{self.title}" on Board "{self.board.title}"'


class Comment(models.Model):
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author.username} on {self.task.title}'
