# cms/admin.py

from django.contrib import admin
from .models import (
    Category, Tag, Course, Article, Video, Post, Documentation,
    Enrollment, Assignment, Quiz, Challenge, Submission,
    UserProgress, PointTransaction, Ranking
)

# =======================
# Inline Admins
# =======================

class ArticleInline(admin.StackedInline):
    model = Article
    fields = ('title', 'author', 'proficiency_level', 'content', 'slug')
    readonly_fields = ('slug',)  # Make slug read-only
    extra = 1  # Number of extra forms to display


class VideoInline(admin.StackedInline):
    model = Video
    fields = ('title', 'author', 'proficiency_level', 'video_url', 'description', 'slug')
    readonly_fields = ('slug',)  # Make slug read-only
    extra = 1


class DocumentationInline(admin.StackedInline):
    model = Documentation
    fields = ('title', 'file', 'slug')
    readonly_fields = ('slug',)  # Make slug read-only
    extra = 1


# =======================
# Model Admins
# =======================

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    prepopulated_fields = {"slug": ("title",)}  # Auto-populate slug from title
    inlines = [ArticleInline, VideoInline, DocumentationInline]
    search_fields = ('title', 'description', 'syllabus')
    list_filter = ('categories', 'tags')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ('name',)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'due_date', 'created_at')
    search_fields = ('title', 'course__title')
    list_filter = ('course',)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'created_at')
    search_fields = ('title', 'course__title')
    list_filter = ('course',)


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'date', 'points')
    search_fields = ('title', 'course__title')
    list_filter = ('course', 'date')


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'assignment', 'quiz', 'challenge', 'submitted_at', 'grade')
    search_fields = ('user__username', 'assignment__title', 'challenge__title', 'quiz__title')
    list_filter = ('submitted_at', 'grade')


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'progress_percentage', 'completed', 'last_updated')
    search_fields = ('user__username', 'course__title')
    list_filter = ('completed', 'last_updated')


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'points', 'description', 'timestamp')
    search_fields = ('user__username', 'description')
    list_filter = ('transaction_type', 'timestamp')


@admin.register(Ranking)
class RankingAdmin(admin.ModelAdmin):
    list_display = ('user', 'points', 'rank')
    search_fields = ('user__username',)
    list_filter = ('rank',)


# =======================
# Register Other Models
# =======================

admin.site.register(Article)
admin.site.register(Video)
admin.site.register(Post)
admin.site.register(Documentation)
admin.site.register(Enrollment)
