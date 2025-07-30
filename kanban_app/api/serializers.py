from rest_framework import serializers
from django.contrib.auth.models import User
from kanban_app.models import Board, Task, Comment


class UserNestedSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']
        read_only_fields = ['id']

    def get_fullname(self, obj):
        return obj.get_full_name()


class TaskNestedSerializer(serializers.ModelSerializer):
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status',
                  'priority', 'due_date', 'comments_count']
        read_only_fields = ['id']

    def get_comments_count(self, obj):
        return Comment.objects.filter(task=obj).count()


class BoardSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ['id', 'title', 'member_count', 'ticket_count',
                  'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id']
        read_only_fields = ['id', 'member_count', 'ticket_count',
                            'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id']

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return Task.objects.filter(board=obj).count()

    def get_tasks_to_do_count(self, obj):
        return Task.objects.filter(board=obj, status='todo').count()

    def get_tasks_high_prio_count(self, obj):
        return Task.objects.filter(board=obj, priority='high').count()


class BoardPartialUpdateSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True
    )
    owner_data = UserNestedSerializer(source='owner_id', read_only=True)
    members_data = UserNestedSerializer(
        source='members', many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'members', 'owner_data', 'members_data']
        read_only_fields = ['id', 'owner_data', 'members_data']


class BoardDetailSerializer(BoardSerializer):
    tasks = TaskNestedSerializer(many=True, read_only=True)
    members = UserNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']
        read_only_fields = ['id']


class TaskSerializer(serializers.ModelSerializer):
    board = serializers.PrimaryKeyRelatedField(
        queryset=Board.objects.all()
    )

    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assignee',
        required=False,
        allow_null=True,
        write_only=True
    )

    assignee = UserNestedSerializer()

    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='reviewer',
        required=False,
        allow_null=True,
        write_only=True
    )
    reviewer = UserNestedSerializer()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'board', 'title', 'description', 'status', 'priority',
                  'assignee_id', 'assignee', 'reviewer_id', 'reviewer', 'due_date', 'comments_count']
        read_only_fields = ['id', 'board', 'comments_count']

    def get_comments_count(self, obj):
        return obj.comments.count()


class TaskPartialUpdateSerializer(TaskSerializer):
    class Meta(TaskSerializer.Meta):
        model = Task
        fields = ['id', 'title', 'description',
                  'status', 'priority', 'assignee_id', 'assignee', 'reviewer_id', 'reviewer', 'due_date']
        read_only_fields = ['id']


class CommentSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(
        read_only=True,
        format='%Y-%m-%dT%H:%M:%SZ'
    )
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']
        read_only_fields = ['id', 'created_at']

    def get_author(self, obj):
        return obj.author.get_full_name()
