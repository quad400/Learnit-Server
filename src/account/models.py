import uuid
from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser
from django.db.models.signals import post_save
from django.utils.text import slugify
from shortuuidfield import ShortUUIDField
from django.template.loader import render_to_string

GENDER_CHOICE = (
    ('male', 'male'),
    ('female', 'female'),
    ('other', 'other'),
)



class UserAccountManager(BaseUserManager):

    def create_user(self, email, fullname, password=None):

        if not email:
            raise ValueError("Email field is required")

        email = self.normalize_email(email)
        user = self.model(email=email, fullname=fullname)
        user.is_instructor = True

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, fullname, password=None):

        user = self.create_user(email, fullname, password)

        user.is_admin = True
        user.is_instructor = True
        user.is_worker = True
        user.save(using=self._db)
        return user


class UserAccount(AbstractBaseUser):
    user_id = ShortUUIDField(editable=False, unique=True)
    email = models.EmailField(unique=True)
    fullname = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_instructor = models.BooleanField(default=False)
    is_worker = models.BooleanField(default=False)

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['fullname']

    def __str__(self):
        return self.fullname

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


class Profile(models.Model):
    profile_id = ShortUUIDField(editable=False, unique=True, primary_key=True)
    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE)
    title = models.CharField(max_length=10, null=True)
    picture = models.ImageField(upload_to="profile/", null=True)
    gender = models.CharField(max_length=10, blank=True,null=True)
    bio = models.TextField(null=True)
    links = models.ManyToManyField('Link', related_name="profile_link", blank=True)
    skills = models.ManyToManyField('Skills', blank=True)
    work_role = models.CharField(max_length=200, null=True)
    slug = models.SlugField()
    location = models.CharField(max_length=250, blank=True, null=True)  
    phone = models.CharField(max_length=20, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.fullname

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = slugify(self.profile_id)
        return super().save(*args, **kwargs)

    def instructor_rating(self):
        return


class Link(models.Model):
    link_id = ShortUUIDField(editable=False, unique=True, primary_key=True)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    link = models.CharField(max_length=250, blank=True)

    def __str__(self):
        return self.link


class Skills(models.Model):
    skill_id = ShortUUIDField(editable=False, unique=True, primary_key=True)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    skill = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name


def create_profile(sender, instance, created, *args, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

post_save.connect(create_profile, sender=UserAccount)


