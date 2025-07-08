from rest_framework import serializers
from kanban_app.models import Board, Task, Comment

class BoardSerializer(serializers.ModelSerializer):
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ['id', 'title', 'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count']
        read_only_fields = ['id', 'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count']

    def get_ticket_count(self, obj):
        return Task.objects.filter(board=obj).count()
    
    def get_tasks_to_do_count(self, obj):
        return Task.objects.filter(board=obj, status='todo').count()
    
    def get_tasks_high_prio_count(self, obj):
        return Task.objects.filter(board=obj, priority='high').count()
    
    
class BoardPartialUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Board
        fields = ['id', 'title']
        read_only_fields = ['id'] 


class TaskOnBoardSerializer(serializers.ModelSerializer):
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority', 'due_date', 'comments_count']
        read_only_fields = ['id']
    
    def get_comments_count(self, obj):
        return Comment.objects.filter(task=obj).count()


class BoardDetailSerializer(BoardSerializer):
    tasks = TaskOnBoardSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'tasks']
        read_only_fields = ['id']


class TaskSerializer(serializers.ModelSerializer):
    board = serializers.PrimaryKeyRelatedField(
        queryset=Board.objects.all()
    )
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'board', 'title', 'description', 'status', 'priority', 'due_date', 'comments_count']
        read_only_fields = ['id', 'board']
        
    def get_comments_count(self, obj):
        return obj.comments.count()
    

class TaskPartialUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority', 'due_date']
        read_only_fields = ['id']


class CommentSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(
        read_only=True,
        format='%Y-%m-%dT%H:%M:%SZ'
    )

    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'content']
        read_only_fields = ['id', 'created_at']
