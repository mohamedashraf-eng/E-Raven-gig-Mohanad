# cms/serializers.py

from rest_framework import serializers
from .models import (
    Article, Video, Post, Documentation, Course,
    Assignment, Quiz, Challenge, Submission,
    UserProgress, PointTransaction, Ranking,
    Category, Tag
)
from django.contrib.auth import get_user_model

User = get_user_model()

# =======================
# Category and Tag Serializers
# =======================

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']

# =======================
# Content Serializers
# =======================

class ArticleSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author = serializers.StringRelatedField()
    
    class Meta:
        model = Article
        fields = ['id', 'title', 'slug', 'content', 'proficiency_level', 'categories', 'tags', 'author']

class VideoSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author = serializers.StringRelatedField()
    
    class Meta:
        model = Video
        fields = ['id', 'title', 'slug', 'video_url', 'description', 'proficiency_level', 'categories', 'tags', 'author']

class PostSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author = serializers.StringRelatedField()
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'slug', 'short_content', 'content', 'proficiency_level', 'categories', 'tags', 'author']

class DocumentationSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author = serializers.StringRelatedField()
    
    class Meta:
        model = Documentation
        fields = ['id', 'title', 'slug', 'file', 'categories', 'tags', 'author']

# =======================
# Course and Related Content Serializers
# =======================

class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['id', 'title', 'description', 'due_date']

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = '__all__'

class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = ['id', 'title', 'description', 'points', 'date']

class CourseSerializer(serializers.ModelSerializer):
    articles = ArticleSerializer(many=True, read_only=True)
    videos = VideoSerializer(many=True, read_only=True)
    assignments = AssignmentSerializer(many=True, read_only=True)
    challenges = ChallengeSerializer(many=True, read_only=True)
    documentations = DocumentationSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'slug', 'description', 'syllabus', 'prerequisites',
                  'categories', 'tags', 'articles', 'videos', 'assignments', 'challenges', 'documentations']

# =======================
# LMS and Progress Serializers
# =======================

class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = '__all__'
        read_only_fields = ['user', 'submitted_at', 'grade']

class UserProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProgress
        fields = '__all__'
        read_only_fields = ['user', 'progress_percentage', 'completed', 'last_updated']

class PointTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointTransaction
        fields = '__all__'
        read_only_fields = ['user', 'timestamp']

class RankingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ranking
        fields = '__all__'

# =======================
# User Serializer
# =======================

class UserSerializer(serializers.ModelSerializer):
    ranking = RankingSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'ranking']
