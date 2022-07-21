from sqlite3 import Timestamp
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from datetime import datetime
from django.core.paginator import Paginator
from django.core import serializers
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from .models import User, Post, Comment, Follow

@login_required
def index(request):
    if request.method =="POST":
        if "new_post" in request.POST:
            new_post = request.POST["new_post_content"]
            author = request.user
            now = datetime.now()
            post_time = now.strftime("%d/%m/%Y %H:%M:%S")

            post = Post.objects.create(content=new_post, author=author,created_at = post_time)
            post.save()

            return HttpResponseRedirect(reverse("index"))

        elif "edit_post" in request.POST:
            print("editpage")
            original_content = request.POST["original_post"]
            new_content = request.POST["edit_content"]
            author=request.user
            now = datetime.now()
            edit_time = now.strftime("%d/%m/%Y %H:%M:%S")

            post = Post.objects.filter(content=original_content).update(content=new_content, updated_at = edit_time)
            return HttpResponseRedirect(reverse("index"))
            #return JsonResponse({'status':'Edit Success'})

        elif "like" in request.POST:
            user=request.user
            content = request.POST["original_post"]
            Post.objects.get(content=content).likes.add(user)
            return HttpResponseRedirect(reverse("index"))

        elif "unlike" in request.POST:
            user=request.user
            content = request.POST["original_post"]
            Post.objects.get(content=content).likes.remove(user)
            return HttpResponseRedirect(reverse("index"))

    else:
        
        all_posts= Post.objects.all()
        all_posts = all_posts.order_by("-id").all()
        user=request.user

        paginator = Paginator(all_posts, 10) #show 10 posts per page

        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        
        return render(request, "network/index.html", {
            
            "posts": all_posts,
            "page_obj": page_obj,
            "user": user

        })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@login_required
def profile(request, profile_user):
    print(profile_user)
    profile_user = User.objects.get(username = profile_user)
    user = request.user

    if request.method =="POST":
     
        if "follow" in request.POST:

            if Follow.objects.filter(user=user).exists():
                new_entry = Follow.objects.get(user=user).following.add(profile_user)
            
            else:    
                new_entry = Follow(user=user)
                new_entry.save()
                new_entry = Follow.objects.get(user=user).following.add(profile_user)
                
                print(Follow.objects.get(user=user).following.count())
                print(Follow.objects.get(user=user).follower.count())

            if Follow.objects.filter(user=profile_user).exists():
                new_entry = Follow.objects.get(user=profile_user).follower.add(user)
            
            else:
                new_entry = Follow(user=profile_user)
                new_entry.save()
                new_entry = Follow.objects.get(user=profile_user).follower.add(user)
            
        elif "unfollow" in request.POST:

            new_entry = Follow.objects.get(user=user).following.remove(profile_user.id)
            new_entry = Follow.objects.get(user=profile_user).follower.remove(user)
        
        elif "like" in request.POST:
            user=request.user
            content = request.POST["original_post"]
            Post.objects.get(content=content).likes.add(user)

        elif "unlike" in request.POST:
            user=request.user
            content = request.POST["original_post"]
            Post.objects.get(content=content).likes.remove(user)

        elif "edit_post" in request.POST:
            print("editpage")
            original_content = request.POST["original_post"]
            new_content = request.POST["edit_content"]
            author=request.user
            now = datetime.now()
            edit_time = now.strftime("%d/%m/%Y %H:%M:%S")

            Post.objects.filter(content=original_content).update(content=new_content, updated_at = edit_time)
        
        return HttpResponseRedirect(reverse("profile", args = [profile_user]))

    else:
        if Follow.objects.filter(user=profile_user).exists():    
            follower_count = Follow.objects.get(user = profile_user).follower.count()
            following_count = Follow.objects.get(user = profile_user).following.count()
        
        else:
            new_entry = Follow(user=profile_user)
            new_entry.save()
            follower_count = Follow.objects.get(user = profile_user).follower.count()
            following_count = Follow.objects.get(user = profile_user).following.count()

        follower = Follow.objects.filter(user = profile_user).values("follower")        
        following = Follow.objects.filter(user = profile_user).values("following")
        user_posts = Post.objects.filter(author = profile_user).order_by("-id").all()

        paginator = Paginator(user_posts, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return render(request, "network/profile.html", {        
                "page_obj": page_obj,
                "profile_user": profile_user,
                "user": user,
                "follower_count": follower_count,
                "following_count": following_count,
                "is_following": follower.filter(follower = user.id).exists()

            })

@login_required
def following(request):

    if request.method =="POST":
        if "like" in request.POST:
            user=request.user
            content = request.POST["original_post"]
            Post.objects.get(content=content).likes.add(user)
            return HttpResponseRedirect(reverse("following"))

        elif "unlike" in request.POST:
            user=request.user
            content = request.POST["original_post"]
            Post.objects.get(content=content).likes.remove(user)
            return HttpResponseRedirect(reverse("following"))
    
    else:
        user=request.user

        if Follow.objects.filter(user=user).exists() != True:
            new_entry = Follow(user=user)
            new_entry.save()

        following = Follow.objects.get(user=user).following
        following_posts = Post.objects.filter(author__in = following.all())
        following_posts = following_posts.order_by("-id").all()

        paginator = Paginator(following_posts, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

            
        return render(request, "network/following.html", {
                
                "posts": following_posts,
                "page_obj": page_obj

            })

@login_required
def post(request, post):

        entry = Post.objects.filter(content = post)
        entry_info = serializers.serialize('json', entry)
        return HttpResponse(entry_info, content_type="text/json-comment-filtered")
        

def allposts(request):
    posts = Post.objects.filter(created_at__isnull=False).order_by("-created_at")
    post_list = serializers.serialize('json', posts)
    return HttpResponse(post_list, content_type="text/json-comment-filtered")



