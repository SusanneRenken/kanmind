from django.contrib.auth.models import User
from django.db import models


class Board(models.Model):
    """
    Represents a Kanban board that contains multiple tasks and members.
    """
    title = models.CharField(max_length=100)
    members = models.ManyToManyField(
        User,
        related_name='boards'
    )
    owner_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_boards'
    )

    def __str__(self):
        """
        Returns the board title for display purposes.
        """
        return self.title


class Task(models.Model):
    """
    Represents a task within a board. Can be assigned to a user and reviewed by another.
    """
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tasks_created'
    )
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    due_date = models.DateField(blank=True, null=True)

    assignee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tasks_assigned',
        null=True,
        blank=True
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tasks_reviewing',
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ('todo', 'To Do'),
            ('in_progress', 'In Progress'),
            ('review', 'Review'),
            ('done', 'Done')
        ],
        default='review'
    )

    priority = models.CharField(
        max_length=10,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High')
        ],
        default='medium'
    )

    def __str__(self):
        """
        Returns a readable string showing task title and its board.
        """
        return f'Task "{self.title}" on Board "{self.board.title}"'


class Comment(models.Model):
    """
    Represents a comment made by a user on a specific task.
    """
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments',
        null=True,
        blank=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        """
        Returns the comment author and task title.
        """
        return f'Comment by {self.author.username} on {self.task.title}'