
from django.urls import path
from . import views

urlpatterns = [    
    path("", views.home, name="home"),
    path("room/<str:pk>/", views.room, name="rooms"),
    path("profile/<str:pk>", views.UserProfile, name="profile"),
    
    path("create-room/", views.createRoom, name="create-room"),
    path("update-room/<str:pk>/", views.UpdateRoom, name="update-room"),
    path("delete-room/<str:pk>/", views.deleteRoom, name="delete-room"),
    path("delete-message/<str:pk>/", views.DeleteMessage, name="delete-message"),
    
    path("login/", views.LoginPage, name="login"),
    path("logout/", views.LogoutUser, name="logout"),
    path("register/", views.RegisterPage, name="register"),
    path("update-user/", views.UpdateUser, name="update-user"),
    
    path("topics/", views.TopicsPage, name="topics"),
    path("activity/", views.ActivitiesPage, name="activity")

    ]