from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User, Follow
from .utils import my_paginator
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required


def index(request):
    post_list = Post.objects.select_related(
        'author', 'group')
    context: dict = {
        'page_obj': my_paginator(post_list, request),
        'title': 'Это главная страница сервиса Yatube',
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author')

    context: dict = {
        'group': group,
        'page_obj': my_paginator(post_list, request),
        'title': 'Записи сообщества ' + f'"{group.title}"'
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('group')
    context = {
        'author': author,
        'page_obj': my_paginator(post_list, request),
        'title': 'Профайл пользователя '
                 + f'{author.first_name} {author.last_name}'
                 + '.',
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author', 'group'),
        pk=post_id,
    )
    comments = post.comments.select_related('author')
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if not post.author == request.user:
        return redirect('posts:post_detail', post_id)
    else:
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'post': post,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)

@login_required
def follow_index(request):
    template = 'posts/follow.html'
    post_list = Post.objects.filter(author__following__user=request.user)
    context = {'page_obj': my_paginator(post_list, request)}
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    if author != user:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    user = request.user
    Follow.objects.filter(user=user, author__username=username).delete()
    return redirect('posts:profile', username=username)
