from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


@cache_page(timeout=20, key_prefix='index_page')
def index(request):
    latest = Post.objects.all()
    paginator = Paginator(latest, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'group': group, 'page': page})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    count_post = author.posts.count()
    post = author.posts.all()
    paginator = Paginator(post, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = None
    if request.user.is_authenticated:
        following = author.following.filter(user=request.user).exists()
    return render(request, 'profile.html', {'author': author,
                                            'count': count_post,
                                            'page': page,
                                            'following': following})


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    comments = post.comments.select_related('author')
    form = CommentForm()
    author = post.author
    count_post = author.posts.count()
    following = None
    if request.user.is_authenticated:
        following = author.following.filter(user=request.user).exists()
    return render(request, 'post.html', {'post': post,
                                         'author': author,
                                         'count': count_post,
                                         'comments': comments,
                                         'form': form,
                                         'following': following})


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        new_comment = form.save(commit=False)
        new_comment.post = post
        new_comment.author = request.user
        new_comment.save()
    return redirect('post', username=request.user, post_id=post_id)


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        new = form.save(commit=False)
        new.author = request.user
        new.save()
        return redirect('index')
    return render(request, 'new.html', {'form': form})


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    author = post.author
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('post', username=request.user, post_id=post_id)
    if author == request.user:
        return render(request, 'edit.html', {'form': form,
                                             'author': author,
                                             'post': post})
    return redirect('index')


@login_required
def follow_index(request):
    post = Post.objects.filter(author__following__user=request.user)
    count_post = post.count()
    paginator = Paginator(post, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {'count': count_post,
                                           'page': page})


@login_required
def profile_follow(request, username):
    if request.user.username == username:
        return redirect('profile', username=request.user)
    author = get_object_or_404(User, username=username)
    Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('profile', username=request.user)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('profile', username=request.user)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
