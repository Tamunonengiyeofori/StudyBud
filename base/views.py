from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Message, Room, Topic, User
from .forms import RoomForm, UserForm, MyUserCreationForm
from django.db.models import Q 
# from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.forms import UserCreationForm
from django.core.mail import send_mail


# Create your views here.

# rooms = [
#     {"id": 1, "name": "Let's learn python!"},
#     {"id": 2, "name": "Design with me"},
#     {"id": 3, "name": "Frontend Developers"},
#     ]

def RegisterPage(request):
    form = MyUserCreationForm()
    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            #customize user submission to retrieve user before saving form
            user = form.save(commit=False)
            #save user's username as lowercase to remove errors
            user.username = user.username.lower()
            user.save()
            #login user automatically after saving user
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "An Error occured during registration")
            
    return render(request, "base/login_register.html", {"form": form})

def LoginPage(request):
    page = "login"
    if request.user.is_authenticated:
        return redirect("home")
    
    if request.method == "POST":
        email = request.POST.get("email").lower()
        password = request.POST.get("password")
        try: 
            user = User.objects.get(email=email)
        except:
            messages.error(request, "User does not exist")
        
        user = authenticate(request, 
                            email=email,
                            password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Username or Password does not exist")
    context = {"page": page}
    return render(request, "base/login_register.html", context)

def LogoutUser(request):
    logout(request)
    return redirect("home")



def home(request):
    #define a variable q that gets the value of the query parameter q for a topic in the url passed in the home template from the request data
    q = request.GET.get("q") if request.GET.get("q") != None else ""
    
    # filter for only rooms with topic name that contains some words of the query parameter q
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | 
        Q(name__icontains=q) | 
        Q(description__icontains=q)
    )
    
    topics = Topic.objects.all()[0:5]
    # the .count() method finds the length of the room Query set
    # The .count() method returns the number of objects in the queryset faster than len()
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    context = {
        "rooms": rooms,
        "topics": topics,
        "room_count": room_count,
        "room_messages": room_messages,
    }
    return render(request, "base/home.html", context)

def room(request, pk):
    room = Room.objects.get(id=pk)  
    room_messages = room.message_set.all().order_by("-created_at")
    participants = room.participants.all()
    
    if request.method == "POST":
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get("body")
        )
        room.participants.add(request.user)
        return redirect("rooms" , pk=room.id)
    
    context = {
        "room_messages": room_messages,
        "room": room,
        "participants": participants,
    }
    
    return render(request, "base/room.html", context)


@login_required(login_url="login")
def createRoom(request):
    form = RoomForm()
    room_topics = Topic.objects.all()
    if request.method == "POST":
        topic_name = request.POST.get("topic") 
        topic, created = Topic.objects.get_or_create(name=topic_name)
        # pass in the post data to the form using request.POST
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get("name"),
            description=request.POST.get("description"),  
        )
        return redirect("home")
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     room = form.save(commit=False) 
        #     room.host = request.user
        #     room.save()
        
    
    context = {"form": form,
               "room_topics": room_topics}
    return render(request, "base/room_form.html", context)


@login_required(login_url="login")
def UpdateRoom(request, pk):
    room = Room.objects.get(id=pk)
    # To prefill the data in the form when updating it, use instance = room in the form
    form = RoomForm(instance=room)
    room_topics = Topic.objects.all()
    
    if request.user != room.host:
        return HttpResponse("You are not authorized to edit this room")
    
    if request.method == "POST":
        # tell the form what room to update using instance = room to pass in post data of an already existing form
        topic_name = request.POST.get("topic") 
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get("name")
        room.topic = topic
        room.description = request.POST.get("description")
        room.save()
        return redirect("home")
        # form  = RoomForm(request.POST, instance=room)
        # if form.is_valid():
        #     form.save()
        
        
    context = {"form": form,
               "room_topics": room_topics,
               "room": room }
    return render(request, "base/room_form.html", context)


@login_required(login_url="login")
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    print(room)
    
    if request.user != room.host:
        return HttpResponse("You are not authorized to delete this room")
       
    if request.method == "POST":
        # print(request.POST)
        room.delete()
        return redirect("home")
    context = {"obj": room}
    return render(request, "base/delete.html", context)


@login_required(login_url="login")
def DeleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    
    if request.user != message.user:
        return HttpResponse("You are not authorized to delete this message")
    
    if request.method == "POST":
        message.delete()
        return redirect("home")
    
    context = {"obj": message}
    
    return render (request, "base/delete.html", context)

# @login_required(login_url="login")
# def UpdateMessage(request, pk):
#     message = Message.objects.get

def UserProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    
    context = {"user": user,
               "rooms": rooms,
               "topics": topics,
               "room_messages": room_messages}
    return render (request , "base/profile.html", context)

@login_required(login_url="login")
def UpdateUser(request):
    user = request.user
    form = UserForm(instance=user)
    
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile', pk=user.id)
    
    context = {"form": form , 
               "user": user}
    return render(request, "base/update-user.html", context)



def TopicsPage(request):
    q = request.GET.get("q") if request.GET.get("q") != None else ""
    topics = Topic.objects.filter(
        name__icontains=q
    )
    context = {"topics": topics}
    return render (request, "base/topics.html", context)
    

def ActivitiesPage(request):
    room_messages = Message.objects.all()
    context = {
        "room_messages": room_messages
    }
    return render (request, "base/activity.html", context) 