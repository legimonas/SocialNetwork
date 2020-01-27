from django.shortcuts import render, redirect
from django.views import View
from .forms import *
from .models import *
# Create your views here.


class PostCreate(View):
    def get(self, request):
        if request.user.is_authenticated:
            return render(request, 'posts/create_post.html')
        else:
            return redirect('home_app:home')

    def post(self, request):
        post_form = PostForm(request.POST, request.FILES)
        print(request.FILES)
        print(request.FILES['attachments'])
        for file in request.FILES:
            print(file)
        return redirect('home_app:home')