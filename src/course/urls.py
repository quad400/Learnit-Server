from django.urls import path

from .views import (
    CourseListAPIView,
    CourseDetailAPIView,CourseUserCreateListAPIView,
    CourseUserRetrieveUpdateDeleteAPIView,CategoryListCreateAPIView,
    CategoryRetrieveUpdateDestroyAPIView,SyllabusListCreateAPIView,
    SyllabusRetrieveUpdateDestroyAPIView,TopicListCreateAPIView,
    TopicRetrieveUpdateDestroyAPIView,InstructorCreateAPIView,
    InstructorDestroyAPIView,InstructorRequestAPIView,
    SkillListCreateAPIView,SkillRetrieveDestroyAPIView,
    FAQListCreateAPIView,FAQRetrieveUpdateDestroyAPIView,
    ReviewListCreateAPIView,DiscussionCreateAPIView,
    QuestionCreateListAPIView,QuestionRetrieveUpdateDestroy,
    QuestionUserListAPIView,AnswerCreateListAPIView,
    AnswerRetrieveUpdateDestroyAPIView,ReplyCreateListAPIView,
    ReplyRetrieveAPIView,LikeUnlikeAnswerCreateAPIView,
    LikeUnlikeReplyCreateAPIView,CourseEnrollAPIView,
    QuizUploadAPIView,FilterByCategoryAPIView,RequirementListCreateAPIView,
    RequirementRetrieveDestroyAPIView,InstructorDetail,ProfileDetail,
    CourseSearchAPIView,FilterByCategoryWithFiterTypeAPIView,CourseFilterByUser,
    SettingsAPIView

    )

urlpatterns = [        
        path('user/<slug:user_id>/',CourseFilterByUser.as_view(), name='course_by_user'),
        path('category/', CategoryListCreateAPIView.as_view(), name='category'), 
        path('category/<slug:pk>/',CategoryRetrieveUpdateDestroyAPIView.as_view(), name='category_id'),
        
        path('user/<slug:user_id>/', InstructorDetail.as_view(), name='instructor'), 
        path('profile/', ProfileDetail.as_view(), name='profile'), 
    
        path('course/<slug:course_id>/syllabus/',SyllabusListCreateAPIView.as_view(),name='course_syllabus'),
        path('course/<slug:course_id>/syllabus/<slug:syllabus_id>/',SyllabusRetrieveUpdateDestroyAPIView.as_view(),name='course_syllabus_id'),
        
        path('course/<slug:course_id>/<slug:syllabus_id>/topic/',TopicListCreateAPIView.as_view(), name='topic_syllabus'),
        path('course/<slug:course_id>/<slug:syllabus_id>/topic/<slug:topic_id>/',TopicRetrieveUpdateDestroyAPIView.as_view(), name='topic_syllabus_id'),
    
        path('course/<slug:course_id>/instructor/request/', InstructorRequestAPIView.as_view(), name="instructor_request"),
        path('course/<slug:course_id>/instructor/<slug:instructor_id>/', InstructorCreateAPIView.as_view(), name="instructor_create"),
        path('course/<slug:course_id>/instructor/<slug:instructor_id>/delete/', InstructorDestroyAPIView.as_view(), name="instructor_create"),
        
        path('course/<slug:course_id>/skill/',SkillListCreateAPIView.as_view(), name='course_skill'),
        path('course/<slug:course_id>/skill/<slug:skill_id>/',SkillRetrieveDestroyAPIView.as_view(), name='course_skill_id'),
        
        path('course/<slug:course_id>/require/',RequirementListCreateAPIView.as_view(), name='require'),
        path('course/<slug:course_id>/require/<slug:requirement_id>/',RequirementRetrieveDestroyAPIView.as_view(), name='require_id'),
        
        path('course/<slug:course_id>/review/',ReviewListCreateAPIView.as_view(), name='course_review'),
        
        path('course/<slug:course_id>/',CourseUserRetrieveUpdateDeleteAPIView.as_view(), name='course_user'),
        path('course/',CourseUserCreateListAPIView.as_view(), name='courses_user'),
        
        path('course/<slug:course_id>/faq/<slug:faq_id>/',FAQRetrieveUpdateDestroyAPIView.as_view(), name='course_faq_id'),
        path('course/<slug:course_id>/faq/',FAQListCreateAPIView.as_view(), name='course_faq'),
        
        path('course/<slug:course_id>/discussion/', DiscussionCreateAPIView.as_view(), name='discussion'),

        path('course/<slug:discussion_id>/questions/',QuestionCreateListAPIView.as_view(), name='questions'),
        path('course/<slug:question_id>/question/',QuestionRetrieveUpdateDestroy.as_view(), name='question'),
        path('course/questions/user/',QuestionUserListAPIView.as_view(), name='question_user'),

        path('course/<slug:question_id>/answers/',AnswerCreateListAPIView.as_view(), name='answers'),
        path('course/<slug:answer_id>/answer/',AnswerRetrieveUpdateDestroyAPIView.as_view(), name='answer'),
        
        path('course/<slug:answer_id>/replys/',ReplyCreateListAPIView.as_view(), name='replys'),
        path('course/<slug:reply_id>/reply/',ReplyRetrieveAPIView.as_view(), name='reply'),
        
        path('course/<slug:answer_id>/answer/like_unlike/',LikeUnlikeAnswerCreateAPIView.as_view(), name='like_unlike'),
        path('course/<slug:reply_id>/reply/like_unlike/',LikeUnlikeReplyCreateAPIView.as_view(), name='reply_like_unlike'),

        path('course/<slug:course_id>/enroll/',CourseEnrollAPIView.as_view(), name='enroll'),

        path('course/<slug:syllabus_id>/quiz_upload/',QuizUploadAPIView.as_view(), name='quiz_upload'),

        path('search/', CourseSearchAPIView.as_view(), name='search'),
        path('<slug:category_id>/category/',FilterByCategoryAPIView.as_view(),name='category__filter_id'),
        path('<slug:category_id>/<slug:sort_by>/',FilterByCategoryWithFiterTypeAPIView.as_view(),name='category__filter'),

        path('',CourseListAPIView.as_view(), name='courses'),
        path('<slug:pk>/',CourseDetailAPIView.as_view(), name='course_detail'),

   ]        

