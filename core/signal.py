from django.db.models.signals import post_save,pre_save
from django.contrib.auth import get_user_model

from account.models import Profile
from course.models import Course, Discussion


User = get_user_model()

def create_profile(sender, instance, created, *args, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

post_save.connect(create_profile, sender=User)


def create_discussion(sender, instance, created, *args, **kwargs):
    if created:
        Discussion.objects.create(course_discuss=instance)

post_save.connect(create_discussion,sender=Course)