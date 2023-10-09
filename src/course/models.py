from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.db.models import Avg,Count
from shortuuidfield import ShortUUIDField

# from shortuuidfield.fields import ShortUUIDField
from quiz.models import Quiz

User = get_user_model()

class Course(models.Model):

    LEVEL = (
        ("Beginner","Beginner"),
        ("Intermediate","Intermediate"),
        ("Advance","Advance"),
        ("General","General"),
    )

    course_id = ShortUUIDField(editable=False, unique=True, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=150, blank=False)
    category = models.ForeignKey("Category", on_delete=models.DO_NOTHING)
    about = models.TextField(blank=True)
    detail = models.TextField(blank=True)
    level = models.CharField(max_length=50, choices=LEVEL,null=True)
    thumbnail = models.ImageField(upload_to='course/',null=True)
    enrolled = models.ManyToManyField(User,through="CourseEnroll",related_name='course_enroll',blank=True)
    intro = models.FileField(upload_to='course_folder', blank=True, null=True)
    instructors = models.ManyToManyField("Instructor",blank=True)
    syllabus = models.ManyToManyField('Syllabus', blank=True)
    price = models.DecimalField(decimal_places=2, max_digits=7)
    previous_price = models.DecimalField(decimal_places=2, max_digits=7, null=True)
    skills = models.ManyToManyField('Skills', blank=True, related_name='my_skills')
    requirement = models.ManyToManyField('Requirement', blank=True, related_name='my_require')
    faqs = models.ManyToManyField('FAQ', blank=True, related_name='my_faq')
    reviews = models.ManyToManyField('Reviews', blank=True, related_name='my_review')
    description = models.TextField(null=True)
    enrolled_counter = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("course")
        verbose_name_plural = _("courses")
        ordering = ['-course_id']
    
    def save(self, *args, **kwargs):
        self.enrolled_counter = self.enrolled.count()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    def get_categories(self):
        category=[]
        if self.category:
            for cat in Category.objects.all():
                category.append(cat)
            return category
        return category

    def average_rate(self):
        rate = Reviews.objects.filter(review_course=self).aggregate(average=Avg('rate'))
        avg=0.0
        if rate['average'] is not None:
            avg=float(rate['average'])
        return float(avg)

    def count_rate(self):
        rate = Reviews.objects.filter(review_course=self).aggregate(count=Count('review_id'))
        count=0
        if rate['count'] is not None:
            count=int(rate['count'])
        return count

    def enrolled_count(self):
        return self.enrolled.count()


class CourseEnrollment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    isEnrolled = models.BooleanField(default=True)

    def get_course_enrolled_user(self):
        return self.user.all()

class Skills(models.Model):
    skill_id = ShortUUIDField(editable=False, unique=True, primary_key=True)
    skill_course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='skil_cours')
    content = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content

class Requirement(models.Model):
    requirement_id = ShortUUIDField(editable=False, unique=True, primary_key=True)
    require_course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='require_cours')
    content = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content


class FAQ(models.Model):
    faq_id = ShortUUIDField(editable=False, unique=True, primary_key=True)
    faq_course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='faq_cours')
    question = models.CharField(max_length=400)
    answer = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question


class Reviews(models.Model):
    review_id = ShortUUIDField(editable=False, unique=True, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    review_course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='review_cours')
    rate = models.IntegerField(default=1)
    comment = models.TextField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user.email


class Instructor(models.Model):
    instructor_id = ShortUUIDField(editable=False, unique=True, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    isLead_instructor = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email


class Syllabus(models.Model):
    syllabus_id = ShortUUIDField(editable=False, unique=True, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    course_syllabus = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_syllabus')
    title = models.CharField(max_length=300, blank=False)
    topics = models.ManyToManyField('Topic', blank=True)
    syllabus_quiz = models.ManyToManyField(Quiz,blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    # def total_quiz_score(self):
    #     if self.syllabus_quiz.none():
    #         return f"{self.title} does not have any quiz to attempt"
    #     else:
    #         score = 0
    #         quiz_attempt = QuizAttempt.objects.filter(user=self.request.user)
    #         if quiz_attempt.exists():
    #             for sc in quiz_attempt:
    #                 score += sc.score
    #             return score
    #         return "Quiz is not attempted"


class Topic(models.Model):
    TOPIC_TYPE = (
        ("Video","Video"), # mkv
        ("Image","Image"), # png ,jpg,jpeg
        ("Document","Document"), # pdf,doc, txt 
    )
    topic_id = ShortUUIDField(editable=False, unique=True, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=400, blank=False)
    topic_type = models.CharField(max_length=50, choices=TOPIC_TYPE, default="Video")
    file = models.FileField(upload_to='course_folder', blank=True, null=True)
    locked = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title


class Category(models.Model):
    category_id = ShortUUIDField(editable=False, unique=True, primary_key=True)
    name = models.CharField(unique=True, max_length=100, blank=False, null=False)

    def __str__(self):
        return self.name

class Discussion(models.Model):
    discussion_id = ShortUUIDField(editable=False, unique=True, primary_key=True)
    course_discuss = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    questions = models.ManyToManyField('Question', blank=True)

def __str__(self):
    return f"{self.course_discuss.title} created by {self.user.email}"

class Question(models.Model):
    question_id = ShortUUIDField(editable=False, unique=True, primary_key=True)
    discuss = models.ForeignKey(Discussion, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    question = models.CharField(max_length=400)
    detail = models.TextField(null=True)
    answers = models.ManyToManyField('Answer', blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question

class Answer(models.Model):
    answer_id = ShortUUIDField(editable=False, unique=True, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    question_answer = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = models.TextField(blank=False)
    reply = models.ManyToManyField('Reply', blank=True)
    like_answer = models.ManyToManyField(User,through='LikeAnswer',related_name='like_me', blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email

class Reply(models.Model):
    reply_id = ShortUUIDField(editable=False, unique=True, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    answer_reply = models.ForeignKey(Answer, on_delete=models.CASCADE,related_name="my_reply")
    like_reply = models.ManyToManyField(User,through='LikeReply',related_name='like_reply_me',blank=True)
    content = models.TextField(blank=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email

class LikeAnswer(models.Model):
    likeanswer_id = ShortUUIDField(editable=False, unique=True, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    answer_like = models.ForeignKey(Answer, on_delete=models.CASCADE,related_name="my_reaction")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email

class LikeReply(models.Model):
    likereply_id = ShortUUIDField(editable=False, unique=True, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    reply_like = models.ForeignKey(Reply, on_delete=models.CASCADE,related_name="my_reaction")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email

class CourseEnroll(models.Model):
    enroll_id = ShortUUIDField(editable=False, unique=True,primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    reply_like = models.ForeignKey(Course, on_delete=models.CASCADE,related_name="my_reaction")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email


class Settings(models.Model):
    logoIcon = models.ImageField(upload_to='settings/',null=True)
    homeBackgroundImg = models.ImageField(upload_to='settings/',null=True)
    bannerImg = models.ImageField(upload_to='settings/',null=True)
    rev1 = models.ImageField(upload_to='settings/',null=True)
    rev2 = models.ImageField(upload_to='settings/',null=True)
    rev3 = models.ImageField(upload_to='settings/',null=True)
    errorImg = models.ImageField(upload_to='settings/',null=True)
