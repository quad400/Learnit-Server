from django.contrib import admin

# Register your models here.
from .models import Quiz,Question,Option,QuizAttempter,AttemtQuestion

admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(QuizAttempter)
admin.site.register(AttemtQuestion)
admin.site.register(Option)