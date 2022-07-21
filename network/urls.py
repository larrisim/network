
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("following", views.following, name="following"),
    path("profile/<str:profile_user>", views.profile, name="profile"),
    path("post/<str:post>", views.post, name="post"),
    path("allposts",views.allposts,name="allposts")
]
