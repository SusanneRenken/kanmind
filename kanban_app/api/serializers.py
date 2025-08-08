from django.contrib.auth.models import User
from rest_framework import serializers
from kanban_app.models import Board, Task, Comment


class UserNestedSerializer(serializers.ModelSerializer):
    """Lightweight user representation for nested usage in tasks/boards."""
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']
        read_only_fields = ['id']

    def get_fullname(self, obj):
        """Return the user's full name (can be empty if not set)."""
        return obj.get_full_name()


class TaskNestedSerializer(serializers.ModelSerializer):
    """
    Compact task representation for embedding in board detail responses.
    Includes assignee/reviewer as nested users and a comments counter.
    """
    comments_count = serializers.SerializerMethodField()
    assignee = UserNestedSerializer(read_only=True)
    reviewer = UserNestedSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'assignee', 'reviewer', 'due_date', 'comments_count'
        ]
        read_only_fields = ['id']

    def get_comments_count(self, obj):
        """Return number of comments attached to this task."""
        return obj.comments.count()


class BoardSerializer(serializers.ModelSerializer):
    """
    Summary serializer for boards used in list views.
    Provides aggregated counts for members, tickets, to-do tasks, and high-priority tasks.
    """
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            'id', 'title', 'member_count', 'ticket_count',
            'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id'
        ]

    def get_member_count(self, obj):
        """Return number of members on the board."""
        return obj.members.count()

    def get_ticket_count(self, obj):
        """Return total number of tasks on the board."""
        return Task.objects.filter(board=obj).count()

    def get_tasks_to_do_count(self, obj):
        """Return number of tasks in 'todo' status on the board."""
        return Task.objects.filter(board=obj, status='todo').count()

    def get_tasks_high_prio_count(self, obj):
        """Return number of high-priority tasks on the board."""
        return Task.objects.filter(board=obj, priority='high').count()


class BoardCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a board. Members are provided as user IDs.
    The owner is injected in the view (create) via `owner_id=request.user`.
    """
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all()
    )

    class Meta:
        model = Board
        fields = ['id', 'title', 'members']
        read_only_fields = ['id']

    def create(self, validated_data):
        """Create board and assign provided members (owner is set in the view)."""
        members = validated_data.pop('members', [])
        owner = validated_data.pop('owner_id', None)
        board = Board.objects.create(owner_id=owner, **validated_data)
        board.members.set(members)
        return board


class BoardPartialUpdateSerializer(serializers.ModelSerializer):
    """
    Partial update for boards: title and members.
    Returns owner/members as nested user data; accepts members as IDs.
    """
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True
    )
    owner_data = UserNestedSerializer(source='owner_id', read_only=True)
    members_data = UserNestedSerializer(source='members', many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'members', 'owner_data', 'members_data']
        read_only_fields = ['id', 'owner_data', 'members_data']

    def update(self, instance, validated_data):
        """Ensure write_only 'members' is applied via .set()."""
        members = validated_data.pop('members', None)
        instance = super().update(instance, validated_data)
        if members is not None:
            instance.members.set(members)
        return instance


class BoardDetailSerializer(BoardSerializer):
    """
    Detailed board view including members and tasks (nested).
    Inherits base counters from BoardSerializer.
    """
    tasks = TaskNestedSerializer(many=True, read_only=True)
    members = UserNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']
        read_only_fields = ['id']


class TaskSerializer(serializers.ModelSerializer):
    """
    Full task serializer used for list/retrieve/create.
    Accepts `assignee_id` and `reviewer_id` to set related users,
    while exposing nested read-only user objects for responses.
    """
    board = serializers.PrimaryKeyRelatedField(queryset=Board.objects.all())

    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assignee',
        required=False,
        allow_null=True,
        write_only=True
    )
    assignee = UserNestedSerializer(read_only=True)

    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='reviewer',
        required=False,
        allow_null=True,
        write_only=True
    )
    reviewer = UserNestedSerializer(read_only=True)

    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status', 'priority',
            'assignee_id', 'assignee', 'reviewer_id', 'reviewer',
            'due_date', 'comments_count'
        ]
        read_only_fields = ['id', 'comments_count']

    def get_comments_count(self, obj):
        """Return number of comments attached to this task."""
        return obj.comments.count()

    def validate(self, attrs):
        """
        Prevent board changes on updates; ensure assignee/reviewer are members (or owner) of the board.
        """
        if self.instance and 'board' in self.initial_data:
            incoming = attrs.get('board')
            if incoming and incoming.pk != self.instance.board.pk:
                raise serializers.ValidationError({'board': 'Changing board is not allowed.'})

        board = attrs.get('board') or (self.instance.board if self.instance else None)

        for field in ('assignee', 'reviewer'):
            user = attrs.get(field)
            if user and board:
                is_member = board.members.filter(pk=user.pk).exists() or board.owner_id == user
                if not is_member:
                    raise serializers.ValidationError({f'{field}_id': 'User must be member or owner of the board.'})
        return attrs


class TaskPartialUpdateSerializer(TaskSerializer):
    """
    Partial update serializer for tasks.
    Exposes only fields that are intended to be mutable after creation.
    """
    class Meta(TaskSerializer.Meta):
        fields = [
            'id', 'title', 'description',
            'status', 'priority',
            'assignee_id', 'assignee',
            'reviewer_id', 'reviewer',
            'due_date'
        ]
        read_only_fields = ['id']


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for task comments.
    Exposes `author` as a human-readable full name string.
    """
    created_at = serializers.DateTimeField(read_only=True, format='%Y-%m-%dT%H:%M:%SZ')
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']
        read_only_fields = ['id', 'created_at']

    def get_author(self, obj):
        """Return the author's full name (fallback to username can be handled outside if needed)."""
        return obj.author.get_full_name()
