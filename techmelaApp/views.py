from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import json

from .models import Project, CustomUser, ProjectLike, ProjectScore


def index(request):
    allProjects = Project.objects.all().order_by('id')
    return render(request, 'techmelaApp/techmela.html', {'allProjects': allProjects})


def logIn(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, "The username and password didn't match. Please try again.")
            return render(request, 'techmelaApp/login.html', {})

    return render(request, 'techmelaApp/login.html')


def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        if CustomUser.objects.filter(username=username).exists():
            messages.info(request, 'Username already in use.')
            return render(request, 'techmelaApp/signup.html', {})

        user = CustomUser(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)

        user.save()

        return redirect('login')

    return render(request, 'techmelaApp/signup.html')


def logOut(request):
    logout(request)
    return redirect('home')


@login_required(login_url='/login')
def markScore(request):
    if request.method == 'POST':
        receivedData = json.loads(request.body)
        score = receivedData['score']
        prjID = receivedData['prjID']
        # score = request.POST.get('score')
        # prjID = request.POST.get('prjID')
        data = {'isSuccess': True, 'alreadySubmitted': False}
        try:
            user = CustomUser.objects.get(username=request.user)
            if user.is_judge:
                try:
                    project = Project.objects.get(id=prjID)
                    if ProjectScore.objects.filter(project=project, judgedBy=user).exists():
                        data['alreadySubmitted'] = True
                        return JsonResponse(data)
                    projectScore = ProjectScore(project=project,score= score, judgedBy=user)
                    projectScore.save()
                    return JsonResponse(data)
                except:
                    print("ERROR in markScore()")
                    data['isSuccess']=False
                    return JsonResponse(data)
        except:
            pass
        pass

    return redirect('home')


@login_required(login_url='/login')
def handleLikes(request):
    if request.method == 'POST':
        receivedData = json.loads(request.body)
        prjID = receivedData['prjID']
        # prjID = request.POST.get('prjIDLike')
        data = {'isSuccess': True, 'isLiked': True}
        try:
            project = Project.objects.get(id=prjID)
            likes = ProjectLike.objects.filter(project=project, likedBy=request.user)
            if likes.exists():
                project.likes-=1
                likes.delete()
                data['isLiked'] = False
            else:
                like = ProjectLike(project= project, likedBy=request.user)
                project.likes += 1
                like.save()
            project.save()
            return JsonResponse(data)
        except:
            print("ERROR in handleLikes()")
            data['isSuccess'] = False
            return JsonResponse(data)


    return redirect('home')
