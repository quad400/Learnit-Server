from django.urls import path

from .views import (QuizView,QuestionView,
                    OptionView,OptionDetailView,
                    QuestionDetailView,QuizDetailView,
                    QuizAttempterView,SubmitAttemptView
                    )

urlpatterns = [
    path('<slug:syllabus_id>/', QuizView.as_view(), name='quiz'),
    path('<slug:pk>/detail/', QuizDetailView.as_view(), name='quiz_detail'),
    path('<slug:quiz_id>/attempt/', QuizAttempterView.as_view(), name='attempt'),
    
    path('<slug:quiz_id>/question/', QuestionView.as_view(), name='question'),
    path('<slug:pk>/question/detail/', QuestionDetailView.as_view(), name='question_detail'),
    
    path('<slug:question_id>/option/', OptionView.as_view(), name='option'),
    path('<slug:pk>/option/detail/', OptionDetailView.as_view(), name='option_detail'),

    path('<slug:question_id>/<slug:option_id>/submit/',SubmitAttemptView.as_view(), name='submit')
    ]

