from django.shortcuts import render, redirect, reverse
from django.views import View
from django.core.files.storage import FileSystemStorage
from users.models import User, UserProfile
from django.http import JsonResponse
from SocialNetwork import settings
from .forms import *
from .models import *
import os


# Create your views here.


class PostCreate(View):
    def get(self, request):
        if request.user.is_authenticated:
            return render(request, 'posts/create_post.html')
        else:
            return redirect('home_app:home')

    def post(self, request):
        post_form = PostForm(request.POST)
        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.creator = request.user
            post.save()
            fs = FileSystemStorage()
            for file in request.FILES.getlist('attachments'):
                filename = fs.save(name=os.path.join('posts_attachments', file.name), content=file)
                name, extension = os.path.splitext(filename)
                attach = Attach(file=filename, post=post, file_extension=extension[1:len(extension)])
                attach.save()
        return redirect('home_app:home')


def get_data_post(post_id, user):
    post = Post.objects.get(id=post_id)
    likes = Post.objects.get(id=post_id).likes.all()
    like_img_url = settings.STATIC_URL + 'images/not_liked.png/'
    if user in likes.all():
        like_img_url = settings.STATIC_URL + 'images/liked.png/'
    return {
        'post': post,
        'creator_profile': UserProfile.objects.get(user=User.objects.get(id=post.creator.id)),
        'attachments': Attach.objects.filter(post_id=post_id).all(),
        'like_img_url': like_img_url,
        'likes': likes
    }


class PostsGet(View):
    def get(self, request, post_id=None):
        if post_id is None:
            posts_list = reversed(Post.objects.order_by('publication_date').all())
            return render(
                request,
                'posts/posts_list.html',
                context={
                    'posts': posts_list,
                    'recommendations_active': '',
                    'articles_active': 'active'
                }
            )
        else:

            return render(
                request,
                'posts/post.html',
                context=get_data_post(post_id, request.user)
            )


class PostLike(View):
    def get(self, request, post_id):
        likes = Post.objects.get(id=post_id).likes
        if request.user.is_authenticated:
            if request.user in likes.all():
                likes.remove(request.user)
            else:
                likes.add(request.user)
        likes_data = {
            "likes_count": likes.count(),
            "likes": [a.email for a in likes.all()]
        }
        return JsonResponse(likes_data)


class PostFunsList(View):
    def get(self, request, post_id):
        post = Post.objects.get(id=post_id)
        profiles = [[UserProfile.objects.get(user=user).avatar, user.email, user.id] for user in post.likes.all()]
        return render(request, 'users/profiles.html', context={'profiles': profiles})


class Recommendations(View):
    def get(self, request):
        if (not request.user.is_authenticated) or not request.user.subscriptions:
            return redirect('posts_app:get')
        else:
            recommended_posts = []
            for profile in request.user.subscriptions.all():
                recommended_posts += Post.objects.filter(creator=User.objects.get(id=profile.user_id)).all()
            return render(
                request,
                'posts/posts_list.html',
                context={
                    'posts': recommended_posts,
                    'recommendations_active': 'active',
                    'articles_active': ''
                }
            )


class GetPostsByUser(View):
    def get(self, request, user_id):
        if not user_id and not request.user.is_authenticated:
            return redirect('home_app:home')
        else:
            buttons = []
            profile_form = None
            if UserProfile.objects.filter(user=User.objects.get(id=user_id)):
                profile_form = UserProfile.objects.get(user=User.objects.get(id=user_id))
            else:
                return render(request, 'users/Message.html', context={
                    'message': 'Данного профиля не существует',
                })
            if request.user.id == user_id \
                    or not profile_form.is_private \
                    or (request.user.is_authenticated and profile_form in request.user.available_profiles.all()):
                return render(request, 'posts/posts_list.html',
                              context={'posts': Post.objects.filter(creator_id=user_id).all()})
            else:
                if request.user.is_authenticated:
                    buttons.append({
                        'url': request.build_absolute_uri(reverse('users_app:perm_req', args=[user_id])),
                        'name': 'Попросить разрешения'
                    })
                return render(request, 'users/Message.html', context={
                    'message': 'У вас нет доступа к этому профилю',
                    'buttons': buttons
                })
