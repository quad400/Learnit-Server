from django.contrib import admin
from django.urls import path, include,re_path
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView
from course.views import SettingsAPIView,SettingsUpdateAPIView,SettingsDetailDeleteAPIView


urlpatterns = [
    path('admin/personal/learnitapp/', admin.site.urls),
    path("auth/", include('djoser.urls')),
    path("auth/", include('djoser.urls.jwt')),
    path('accounts/', include('account.urls')),
    path('courses/',include('course.urls')),
    path('quiz/',include('quiz.urls')),
    path('order/',include('order.urls')),
]


urlpatterns += [
    path('settings/', SettingsAPIView.as_view(), name='settings'),
    path('settings/<int:pk>/', SettingsDetailDeleteAPIView.as_view(), name='settings_detail'),
    path('settings/<int:pk>/', SettingsUpdateAPIView.as_view(), name='settings_detail')
] 

# urlpatterns += [re_path(r'^.*', TemplateView.as_view(template_name='index.html'))]

urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)