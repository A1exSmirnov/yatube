from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.SELECT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = 'Последние обновления на сайте'
    context = {
        'page_obj': page_obj,
        'title': title,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):

    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, settings.SELECT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = f'Записи сообщества {group.title}'
    context = {
        'group': group,
        'page_obj': page_obj,
        'title': title,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, settings.SELECT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    count = author.posts.count()
    context = {
        'page_obj': page_obj,
        'count': count,
        'author': author,
    }
    following_list = author.following.all()
    for follow in following_list:
        if follow.user == request.user:
            context['following'] = True
        else:
            context['following'] = False
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post_detail = get_object_or_404(Post, id=post_id)
    count = post_detail.author.posts.count()
    form = CommentForm(request.POST or None)
    comments = post_detail.comments.all()
    context = {
        'count': count,
        'post_detail': post_detail,
        'form': form,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        username = request.user.username
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("posts:profile", username)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post
                    )
    if post.author == request.user:
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:post_detail', post_id=post_id)
        context = {
            'form': form,
            'is_edit': True
        }
        return render(request, "posts/create_post.html", context)
    else:
        return redirect('/')


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    followers = Follow.objects.filter(user=request.user)
    author_list = []
    for follower in followers:
        author_list.append(follower.author)
    post_list = Post.objects.filter(author__in=author_list)
    paginator = Paginator(post_list, settings.SELECT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = 'Список постов авторов'
    context = {
        'page_obj': page_obj,
        'title': title,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    following_list = author.following.all()
    follower = []
    for follow in following_list:
        follower.append(follow.user)
    if author != request.user:
        if request.user in follower:
            return redirect('posts:profile', username)
        else:
            follow_new = Follow()
            follow_new.user = request.user
            follow_new.author = author
            follow_new.save()
            return redirect('posts:profile', username)
    else:
        return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    following = get_object_or_404(Follow, author=author)
    following.delete()
    return redirect('posts:profile', username)
