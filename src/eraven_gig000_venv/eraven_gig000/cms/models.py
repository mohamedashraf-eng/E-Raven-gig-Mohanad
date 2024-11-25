# cms/models.py

from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse

User = settings.AUTH_USER_MODEL

# =======================
# CMS Models
# =======================

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ContentBase(models.Model):
    PROFICIENCY_LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, editable=False)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)s_contents'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField(
        Category,
        related_name='%(class)s_contents'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='%(class)s_contents',
        blank=True
    )
    proficiency_level = models.CharField(
        max_length=50,
        choices=PROFICIENCY_LEVEL_CHOICES
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class Course(models.Model):
    PROFICIENCY_LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    syllabus = models.TextField()
    prerequisites = models.TextField(blank=True, null=True)
    proficiency_level = models.CharField(max_length=50, default=1, choices=PROFICIENCY_LEVEL_CHOICES)
    categories = models.ManyToManyField(Category)
    tags = models.ManyToManyField(Tag)
    picture = models.ImageField(upload_to='course_pics/', blank=True, null=True, help_text="Image for the course")
    instructor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses_instructed',
        help_text="Instructor responsible for the course"
    )
    points = models.PositiveIntegerField(help_text="Points awarded for completing the course", default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Session(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='sessions',
        help_text="The course that this session belongs to"
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    meeting_link = models.URLField(blank=True, null=True, help_text="URL for the session meeting (e.g., Zoom link)")
    date_time = models.DateTimeField(blank=True, null=True, help_text="Date and time of the session")
    instructor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sessions_instructed',
        help_text="Instructor responsible for the session"
    )
    content = models.TextField(help_text="Content or description of the session")
    categories = models.ManyToManyField(Category)
    tags = models.ManyToManyField(Tag, blank=True)
    points = models.PositiveIntegerField(help_text="Points awarded for attending the session", default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_detail_url(self):
        return reverse('cms:session_detail', args=[self.course.slug, self.id])
    
    def __str__(self):
        return f"{self.title} - {self.course.title}"

class Workshop(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='workshops'
    )
    points_cost = models.PositiveIntegerField(
        help_text="Points required to attend the workshop",
        default=25
    )
    description = models.TextField()
    meeting_link = models.URLField(
        help_text="URL for the workshop meeting (e.g., Zoom link)"
    )
    date_time = models.DateTimeField(help_text="Date and time of the workshop")
    instructor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='workshops_instructed',
        help_text="Instructor responsible for the workshop"
    )
    duration = models.DurationField(
        default=60,
        help_text="Duration of the workshop (e.g., 2 hours)"
    )
    picture = models.ImageField(
        upload_to='workshop_pics/', blank=True, null=True,
        help_text="Image for the workshop"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField(Category)
    tags = models.ManyToManyField(Tag, blank=True)
    points = models.PositiveIntegerField(
        help_text="Points awarded for attending the workshop",
        default=0
    )

    class Meta:
        ordering = ['date_time']

    def get_detail_url(self):
        return reverse('cms:workshop_detail', args=[self.course.slug, self.id])
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.course.title})"


class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    proficiency_level = models.CharField(max_length=50, choices=ContentBase.PROFICIENCY_LEVEL_CHOICES)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='articles', default=1)  # Default value for migration
    categories = models.ManyToManyField(Category)
    tags = models.ManyToManyField(Tag)
    points = models.PositiveIntegerField(
        help_text="Points awarded for reading the article",
        default=0
    )

    def get_detail_url(self):
        return reverse('cms:article_detail', args=[self.course.slug, self.id])
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Video(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    video_url = models.URLField()
    description = models.TextField()
    proficiency_level = models.CharField(max_length=50, choices=ContentBase.PROFICIENCY_LEVEL_CHOICES)
    categories = models.ManyToManyField(Category)
    tags = models.ManyToManyField(Tag)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='videos', default=1)  # Default value for migration
    points = models.PositiveIntegerField(
        help_text="Points awarded for watching the video",
        default=0
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_detail_url(self):
        return reverse('cms:video_detail', args=[self.course.slug, self.id])
    
    def __str__(self):
        return self.title


class Post(ContentBase):
    slug = models.SlugField(unique=True, blank=True)  # Ensure slug is defined
    short_content = models.TextField()
    content = models.TextField()
    points = models.PositiveIntegerField(
        help_text="Points awarded for reading the post",
        default=0
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Documentation(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    file = models.FileField(upload_to='docs/')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='documentations', default=1)  # Default value for migration
    categories = models.ManyToManyField(Category)
    tags = models.ManyToManyField(Tag)
    points = models.PositiveIntegerField(
        help_text="Points awarded for reading the documentation",
        default=0
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')  # Prevent duplicate enrollments

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"


# =======================
# LMS Models
# =======================

class TimelineEvent(models.Model):
    EVENT_TYPES = [
        ('course', 'Course Meeting'),
        ('session', 'Session Meeting'),
        ('assignment', 'Assignment Deadline'),
        ('quiz', 'Quiz Deadline'),
        ('workshop', 'Workshop Meeting'),
        ('challenge_start', 'Challenge Start'),
        ('challenge_deadline', 'Challenge Deadline'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='timeline_events')
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    event_date = models.DateTimeField()

    class Meta:
        ordering = ['event_date']
        unique_together = ('user', 'event_type', 'content_type', 'object_id')

    def __str__(self):
        return f"{self.get_event_type_display()} - {self.content_object.title} on {self.event_date}"
    

class Assignment(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='assignments',
        default=1  # Default value for migration
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()
    link = models.URLField(
        blank=True,
        null=True,
        help_text="URL to access or submit the assignment form"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    points = models.PositiveIntegerField(
        help_text="Points awarded for completing the assignment",
        default=0
    )
    def get_detail_url(self):
        return reverse('cms:assignment_detail', args=[self.course.slug, self.id])


    def __str__(self):
        return f"{self.title} ({self.course.title})"

class Quiz(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='quizzes',
        default=1  # Default value for migration
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField(default=timezone.now)  # Set default to timezone.now
    link = models.URLField(
        blank=True,
        null=True,
        help_text="URL to access or submit the quiz form"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    points = models.PositiveIntegerField(
        help_text="Points awarded for completing the quiz",
        default=0
    )
    def get_detail_url(self):
        return reverse('cms:quiz_detail', args=[self.course.slug, self.id])
    
    def __str__(self):
        return f"{self.title} ({self.course.title})"


class Challenge(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    picture = models.ImageField(upload_to='challenge_pics/', blank=True, null=True, help_text="Image for the course")
    date = models.DateField(default=timezone.now)
    due_date = models.DateTimeField(default=timezone.now)  # Set default to timezone.now
    points = models.PositiveIntegerField(default=10)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='challenges', default=1)  # Default value for migration
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('title', 'date')
    def get_detail_url(self):
        return reverse('cms:challenge_detail', args=[self.id])
    
    def __str__(self):
        return f"{self.title} on {self.date}"

class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    grade = models.IntegerField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    # GenericForeignKey fields
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"Submission by {self.user} for {self.content_object}"

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')

class UserProgress(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='progresses'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='progresses',
        default=1  # Default value for migration
    )
    completed = models.BooleanField(default=False)
    progress_percentage = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.username} - {self.course.title} Progress"


class PointTransaction(models.Model):
    POINTS_CHOICES = [
        ('earn', 'Earned'),
        ('spend', 'Spent'),
    ]
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='point_transactions'
    )
    transaction_type = models.CharField(max_length=10, choices=POINTS_CHOICES)
    points = models.IntegerField()
    description = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_transaction_type_display()} {self.points} points"


class Ranking(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ranking')
    points = models.IntegerField(default=0)
    rank = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - Rank {self.rank} - {self.points} Points"

    class Meta:
        ordering = ['-points']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_rank()

    def update_rank(self):
        rankings = Ranking.objects.order_by('-points')
        for idx, ranking in enumerate(rankings, start=1):
            if ranking.rank != idx:
                Ranking.objects.filter(pk=ranking.pk).update(rank=idx)

class ArticleRead(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='articles_read'
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='reads'
    )
    read_at = models.DateTimeField(auto_now_add=True)
    points_awarded = models.PositiveIntegerField(
        help_text="Points awarded for reading the article",
        default=0
    )

    class Meta:
        unique_together = ('user', 'article')  # Prevent multiple reads awarding points multiple times

    def __str__(self):
        return f"{self.user.username} read {self.article.title}"


class DocumentationRead(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='documentations_read'
    )
    documentation = models.ForeignKey(
        Documentation,
        on_delete=models.CASCADE,
        related_name='reads'
    )
    read_at = models.DateTimeField(auto_now_add=True)
    points_awarded = models.PositiveIntegerField(
        help_text="Points awarded for reading the documentation",
        default=0
    )

    class Meta:
        unique_together = ('user', 'documentation')  # Prevent multiple reads awarding points multiple times

    def __str__(self):
        return f"{self.user.username} read {self.documentation.title}"