from django.urls import path
from . import views

urlpatterns = [
    path('api/v1/pending_approvals', views.UserApprovalAPIView.as_view(), name="pending_approvals"),
    path('api/v1/sign_up', views.RegistrationAPIView.as_view(), name="register"),
    path('api/v1/sign_in', views.LoginAPIView.as_view(), name="login"),
    path('api/v1/logout', views.LogoutView.as_view(), name="logout"),
    path('signup/', views.RegistrationAPIView.as_view(), name="signup"),
    path('', views.index_view, name='index'),
]