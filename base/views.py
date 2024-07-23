from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User 
from django.contrib.auth import authenticate, login, logout  
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic
from .forms import RoomForm

def login_page(request):
    page_name = 'login'
    
    if request.user.is_authenticated:
        return redirect("home")
    
    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "User does not exist!")
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Username and password not matching!")
        
    context = {"page": page_name}
    return render(request, "base/login_register.html", context)

def register_page(request):
    if request.user.is_authenticated:
        return redirect("home")
    
    page_name = 'register'
    form = UserCreationForm()
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Form is not valid!")
    
    context = {"page": page_name, 'form': form}
    return render(request, "base/login_register.html", context)

def logout_user(request):
    logout(request)
    return redirect('home')

def home(request):
    q = request.GET.get('q')
    
    rooms = Room.objects.filter(
        Q(topic__name__contains=q) |
        Q(name__contains=q) |
        Q(description__icontains=q) |
        Q(host__username__contains=q)
        ) if q != None  else Room.objects.all()
    
    topics = Topic.objects.all()
    room_count = rooms.count()
    
    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    
    context = {'room': room, 'room_messages':room_messages}
    return render(request, 'base/room.html', context)

@login_required(login_url='/login')
def create_room(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
            
    context = {'form': form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='/login')
def update_room(request, pk):
    room = Room.objects.get(id=int(pk))
    form = RoomForm(instance=room)
    
    if request.user != room.host:
        return HttpResponse("Forbidden")
    
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
    
    context = {'form': form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='/login')
def delete_room(request, pk):
    room = Room.objects.get(id=int(pk))
    
    if request.user != room.host:
        return HttpResponse("Forbidden")
    
    if request.method == "POST":
        room.delete()
        return redirect("home")
    
    return render(request, 'base/delete.html', {'object':room})