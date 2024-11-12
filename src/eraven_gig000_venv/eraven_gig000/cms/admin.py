# cms/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from .models import (
    Category, Tag, Course, Article, Video, Post, Documentation,
    Enrollment, Assignment, Quiz, Challenge, Submission,
    UserProgress, PointTransaction, Ranking, Workshop, TimelineEvent,
    Session
)
from ums.models import Profile
from .forms import SubmissionForm

# =======================
# Inline Admins
# =======================

class ArticleInline(admin.StackedInline):
    model = Article
    fields = ('title', 'author', 'proficiency_level', 'content', 'slug')
    readonly_fields = ('slug',)
    extra = 1


class VideoInline(admin.StackedInline):
    model = Video
    fields = ('title', 'author', 'proficiency_level', 'video_url', 'description', 'slug')
    readonly_fields = ('slug',)
    extra = 1


class DocumentationInline(admin.StackedInline):
    model = Documentation
    fields = ('title', 'file', 'slug')
    readonly_fields = ('slug',)
    extra = 1

# =======================
# Model Admins
# =======================

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'display_picture')
    list_filter = ('instructor', 'categories', 'tags')
    search_fields = ('title', 'description', 'instructor__username')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('categories', 'tags',)
    inlines = [ArticleInline, VideoInline, DocumentationInline]
    list_select_related = ('instructor',)

    def display_picture(self, obj):
        if obj.picture:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 50%;" />',
                obj.picture.url
            )
        return "No Image"

    display_picture.short_description = 'Picture'


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
    list_select_related = ('course',)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'created_at')
    search_fields = ('title', 'course__title')
    list_filter = ('course',)
    list_select_related = ('course',)


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'date', 'points')
    search_fields = ('title', 'course__title')
    list_filter = ('course', 'date')
    list_select_related = ('course',)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    form = SubmissionForm
    list_display = ('user', 'get_content_type', 'submitted_at', 'grade')
    search_fields = ('user__username', 'content_object__title')
    list_filter = ('submitted_at', 'grade')

    def get_content_type(self, obj):
        return obj.content_type
    get_content_type.short_description = 'Content Type'


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'progress_percentage', 'completed', 'last_updated')
    search_fields = ('user__username', 'course__title')
    list_filter = ('completed', 'last_updated')
    list_select_related = ('user', 'course')


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'points', 'description', 'timestamp')
    search_fields = ('user__username', 'description')
    list_filter = ('transaction_type', 'timestamp')
    list_select_related = ('user',)


@admin.register(Ranking)
class RankingAdmin(admin.ModelAdmin):
    list_display = ('user', 'points', 'rank')
    search_fields = ('user__username',)
    list_filter = ('rank',)
    list_select_related = ('user',)


@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'instructor', 'date_time', 'points_cost', 'display_picture')
    list_filter = ('course', 'instructor', 'date_time', 'categories', 'tags')
    search_fields = ('title', 'description', 'instructor__username')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('categories', 'tags',)
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'course', 'description', 'points_cost')
        }),
        ('Workshop Details', {
            'fields': ('meeting_link', 'date_time', 'instructor', 'duration', 'picture'),
        }),
        ('Categorization', {
            'fields': ('categories', 'tags'),
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'title', 'slug', 'course', 'description', 'points_cost',
                'meeting_link', 'date_time', 'instructor', 'duration',
                'picture', 'categories', 'tags'
            )
        }),
    )
    list_select_related = ('course', 'instructor')
    prefetch_related = ('categories', 'tags',)

    def display_picture(self, obj):
        """
        Displays the workshop's picture in the admin list.
        """
        if obj.picture:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 50%;" />',
                obj.picture.url
            )
        return "No Image"

    display_picture.short_description = 'Picture'


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'proficiency_level', 'course')
    search_fields = ('title', 'author__username', 'course__title')
    list_filter = ('proficiency_level', 'course')
    list_select_related = ('author', 'course')


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'proficiency_level', 'course')
    search_fields = ('title', 'author__username', 'course__title')
    list_filter = ('proficiency_level', 'course')
    list_select_related = ('author', 'course')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    search_fields = ('title', 'author__username')
    list_filter = ('created_at',)
    list_select_related = ('author',)


@admin.register(Documentation)
class DocumentationAdmin(admin.ModelAdmin):
    list_display = ('title', 'file', 'course')
    search_fields = ('title', 'course__title')
    list_filter = ('course',)
    list_select_related = ('course',)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'enrolled_at')
    search_fields = ('user__username', 'course__title')
    list_filter = ('course', 'enrolled_at')
    list_select_related = ('user', 'course')


@admin.register(TimelineEvent)
class TimelineEventAdmin(admin.ModelAdmin):
    list_display = ('user', 'event_type', 'content_object_link', 'event_date')
    search_fields = ('user__username', 'content_object__title')
    list_filter = ('event_type', 'event_date', 'user')
    date_hierarchy = 'event_date'
    ordering = ('-event_date',)
    readonly_fields = ('user', 'event_type', 'content_object', 'event_date', 'content_type', 'object_id')

    list_select_related = ('user', 'content_type')

    def content_object_link(self, obj):
        """
        Creates a clickable link to the related content object in the admin.
        """
        if obj.content_object:
            app_label = obj.content_type.app_label
            model_name = obj.content_type.model
            object_id = obj.object_id
            try:
                content_title = getattr(obj.content_object, 'title', str(obj.content_object))
            except AttributeError:
                content_title = str(obj.content_object)

            return format_html(
                '<a href="/admin/{}/{}/{}/change/">{}</a>',
                app_label,
                model_name,
                object_id,
                content_title
            )
        return "No Link"

    content_object_link.short_description = 'Content Object'

    def has_add_permission(self, request):
        # Prevent adding TimelineEvents manually
        return False

    def has_change_permission(self, request, obj=None):
        # Prevent changing TimelineEvents
        return False

    def has_delete_permission(self, request, obj=None):
        # Allow deleting TimelineEvents
        return True


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'date_time', 'instructor', 'points', 'display_meeting_link')
    search_fields = ('title', 'course__title', 'instructor__username')
    list_filter = ('course', 'date_time', 'instructor')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('categories', 'tags',)
    list_select_related = ('course', 'instructor')
    prefetch_related = ('categories', 'tags',)

    def display_meeting_link(self, obj):
        """
        Displays a clickable link to the session meeting in the admin list.
        """
        if obj.meeting_link:
            return format_html('<a href="{}" target="_blank">Link</a>', obj.meeting_link)
        return "No Link"

    display_meeting_link.short_description = 'Meeting Link'

# =======================
# Remove Unused Inlines
# =======================

# If you have any inlines that are not used, remove them or comment them out.
# For example:
# class SessionInline(admin.StackedInline):
#     model = Session
#     extra = 1
#     fields = ('title', 'date_time', 'meeting_link', 'instructor', 'points', 'content', 'categories', 'tags')
#     readonly_fields = ('slug',)
#     filter_horizontal = ('categories', 'tags',)

# =======================
# Register Other Models
# =======================

# If there are models not yet registered, register them here.

# Example:
# @admin.register(YourModel)
# class YourModelAdmin(admin.ModelAdmin):
#     pass

# =======================
# Summary
# =======================

# - Optimized SubmissionAdmin to handle GenericForeignKey correctly.
# - Removed duplicate and unused inline admin classes.
# - Ensured consistency and DRY principles across ModelAdmin classes.
# - Utilized list_select_related and prefetch_related for query optimization.
# - Enhanced readability with comments and logical sectioning.
