from django.contrib import admin

from .models import (
                    Course,Category,Syllabus,Discussion,
                    Question,Answer,Reply,Reviews,Skills,Topic
                )

class CourseAdmin(admin.ModelAdmin):
    list_display = [ "title","category","price"]
    list_display_links = ["title"]
    readonly_fields = ("course_id", "user","price",)


admin.site.register(Course,CourseAdmin)
admin.site.register(Category)
admin.site.register(Question)
admin.site.register(Discussion)
admin.site.register(Answer)
admin.site.register(Reply)
admin.site.register(Syllabus)
admin.site.register(Topic)
admin.site.register(Skills)
admin.site.register(Reviews)
