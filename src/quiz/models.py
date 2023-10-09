from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save

from shortuuidfield import ShortUUIDField

# from course.models import Syllabus

User = get_user_model()

class Option(models.Model):
    option_id = ShortUUIDField(editable=False, max_length=10, primary_key=True,unique=True)
    option = models.CharField(max_length=500)
    correct = models.BooleanField(default=False)
    quest = models.ForeignKey('Question', on_delete=models.CASCADE)

    def __str__(self):
        return self.option

class Question(models.Model):
    question_id = ShortUUIDField(editable=False, max_length=10, primary_key=True,unique=True)
    quiz = models.ForeignKey('Quiz', on_delete=models.CASCADE)
    question = models.CharField(max_length=500)
    opt = models.ManyToManyField(Option, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question

class AttemtQuestion(models.Model):
    question_id = ShortUUIDField(editable=False, max_length=10, primary_key=True,unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quest = models.ForeignKey(Question, on_delete=models.CASCADE)
    answered = models.BooleanField(default=False)

    def __str__(self):
        return self.user.fullname

class Quiz(models.Model):
    quiz_id = ShortUUIDField(editable=False, max_length=10, primary_key=True,unique=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=100)
    quizs = models.ManyToManyField(Question, blank=True, related_name="my_quiz")

    def __str__(self):
        return self.title


class QuizAttempter(models.Model):
    attempter_id = ShortUUIDField(editable=False, max_length=10, primary_key=True,unique=True)
    user_attempt = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=0)
    quizz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.user_attempt.fullname