from django.urls import path

from .views import (
            UserListAPIView,
            UserAPIView,
            LinkAPIView,
            LinkRetrieveUpdateDestroyAPIView,
            ProfileDetailUpdate,
            SkillAPIView,
            SkillRetrieveUpdateDestroyAPIView,
            UserCreateAPI,
            ActivationAPI,
            GoogleLoginApi,
            GoogleLoginRedirectApi,
            SendEmailAPIView
        )

urlpatterns = [
    path('user/<slug:pk>/', UserAPIView.as_view(), name='user'),
    path('', UserListAPIView.as_view(), name='user_list'),
    path('create/user/', UserCreateAPI.as_view()),
    path("callback/", GoogleLoginApi.as_view(), name="callback-raw"),
    path("redirect/", GoogleLoginRedirectApi.as_view(), name="redirect-raw"),
    path('activate/', ActivationAPI.as_view()),
    path('forget_password/', SendEmailAPIView.as_view(), name='send-email'),

    path('profile/', ProfileDetailUpdate.as_view(), name='profile'),

    path('user/<slug:profile_id>/skill/', SkillAPIView.as_view(), name='skill'),
    path('user/<slug:profile_id>/<slug:skill_id>/', SkillRetrieveUpdateDestroyAPIView.as_view(),name='skill_id'),

    path('user/<slug:profile_id>/link/', LinkAPIView.as_view(), name='link'),
    path('user/<slug:profile_id>/<slug:link_id>/', LinkRetrieveUpdateDestroyAPIView.as_view(),name='link_id'),

]
{
'http://127.0.0.1:8000/auth/users/': "create_user",
'http://127.0.0.1:8000/auth/jwt/create': "login_user",
'http://127.0.0.1:8000/auth/users/activation/':'activate account',
'http://127.0.0.1:8000/auth/users/resend_activation/': 'resend activation',
'http://127.0.0.1:8000/auth/users/me/':"delete update get"
}