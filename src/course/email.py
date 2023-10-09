from templated_mail.mail import BaseEmailMessage
from django.shortcuts import render
from .models import Course

class InstructorRequestEmail(BaseEmailMessage):
    template_name = "email/instructor_request.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
