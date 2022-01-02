from django.urls import re_path, include
from django.contrib import admin


from rest_framework import routers

from api import views
from blog import views as BlogViews

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'posts', views.PostViewSet)
router.register(r'case-studies', views.CaseStudyViewSet)
router.register(r'highlighted-case-studies', views.HighlightedCaseStudyViewSet)

urlpatterns = [
    re_path(r'^admin-cool/', admin.site.urls),
    re_path(r'^django-health-check/$', BlogViews.HealthCheckView.as_view(), name='django-health-check'),
    re_path(r'^fail-test/$', BlogViews.FailView.as_view(), name='fail-test'),

    re_path(r'^report', BlogViews.EmailView.as_view(), name='report'),
    re_path(r'^recaptcha/$', BlogViews.ContactMeView.as_view(), name='recaptcha'),

    # re_path(r'^ckeditor/', include('ckeditor_uploader.urls')),
    re_path(r'^api/uploads/', views.FileUploadView.as_view()),

    re_path(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')), # for the browsable API login URLs
    re_path(r'^api/token-auth/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # for the browsable API login URLs
    re_path(r'^api/token-refresh/', TokenRefreshView.as_view(), name='token_refresh'), # for the browsable API login URLs
    re_path(r'^api/', include(router.urls)),

    re_path(r'^.*$', views.APIIndexView.as_view()),
]