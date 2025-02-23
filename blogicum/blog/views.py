from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.utils.timezone import now
from .models import Post, Category, Comment
from django.contrib.auth import get_user_model
from .forms import PostForm, CommentForm, UserForm
from django.core.paginator import Paginator
from django.db.models import Count
from django.contrib.auth.decorators import login_required


User = get_user_model()


def filter_posts(posts):
    return posts.annotate(comment_count=Count('comments')).filter(
        Q(pub_date__lte=now())
        & Q(is_published=True)
        & Q(category__is_published=True)
    ).order_by(
        "-pub_date"
    )


def paginator_page(list, count, request):
    paginator = Paginator(list, count)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    template_name = 'blog/index.html'
    posts = filter_posts(
        Post.objects.select_related('category', 'author', 'location')
    )
    page_obj = paginator_page(posts, 10, request)
    context = {'page_obj': page_obj}
    return render(request, template_name, context)


def post_detail(request, post_id):
    template_name = 'blog/detail.html'

    post = get_object_or_404(Post.objects.select_related(
        'category', 'author', 'location'), pk=post_id)
    if request.user != post.author:
        post = get_object_or_404(
            filter_posts(
                Post.objects.select_related('category', 'author', 'location')
            ),
            pk=post_id
        )
    comments = post.comments.select_related('author')
    context = {
        'post': post,
        'form': CommentForm(),
        'comments': comments,

    }
    return render(request, template_name, context)


def category_posts(request, category_slug):
    template_name = 'blog/category.html'
    category = get_object_or_404(
        Category.objects.filter(is_published=True),
        slug=category_slug
    )
    posts = filter_posts(
        category.posts.select_related('category', 'author', 'location')
    )
    page_obj = paginator_page(posts, 10, request)
    context = {
        'category': category,
        'page_obj': page_obj
    }
    return render(request, template_name, context)


def user_profile(request, username):
    template_name = 'blog/profile.html'
    profile = get_object_or_404(User.objects, username=username)
    posts = (
        profile.posts
        .annotate(comment_count=Count('comments'))
        .select_related('category', 'author', 'location')
        .order_by("-pub_date")
    )

    page_obj = paginator_page(posts, 10, request)
    context = {
        'profile': profile,
        'page_obj': page_obj,
    }
    return render(request, template_name, context)


def edit_profile(request):
    template_name = 'blog/user.html'
    username = request.user.get_username()
    instance = get_object_or_404(User, username=username)
    form = UserForm(request.POST or None, instance=instance)
    context = {'form': form}
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=username)
    return render(request, template_name, context)


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id=pk)


@login_required
def create_post(request):
    template = 'blog/create.html'

    form = PostForm(request.POST or None, request.FILES or None)

    context = {'form': form}
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('blog:profile', username=request.user.get_username())

    return render(request, template, context)


@login_required
def edit_post(request, post_id):
    template_name = 'blog/create.html'
    instance = get_object_or_404(Post, pk=post_id)

    if request.user != instance.author:
        return redirect('blog:post_detail', post_id=post_id)

    form = PostForm(request.POST or None,
                    request.FILES or None, instance=instance)

    context = {'form': form}
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('blog:post_detail', post_id=post_id)

    return render(request, template_name, context)


@login_required
def edit_comment(request, post_id, comment_id):
    template_name = 'blog/comment.html'
    instance = get_object_or_404(Comment, pk=comment_id)
    if request.user != instance.author:
        return redirect('blog:post_detail', post_id=post_id)

    form = CommentForm(request.POST or None, instance=instance)

    context = {
        'form': form,
        'comment': instance,
    }
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('blog:post_detail', post_id=post_id)

    return render(request, template_name, context)


@login_required
def delete_post(request, post_id):
    template_name = 'blog/create.html'
    instance = get_object_or_404(Post, pk=post_id)
    if request.user != instance.author:
        return redirect('blog:post_detail', post_id=post_id)
    form = PostForm(instance=instance)
    context = {'form': form}
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:profile', username=request.user)
    return render(request, template_name, context)


@login_required
def delete_comment(request, post_id, comment_id):
    template_name = 'blog/comment.html'
    instance = get_object_or_404(Comment, pk=comment_id)
    if request.user != instance.author:
        return redirect('blog:post_detail', post_id=post_id)
    context = {'comment': instance}
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, template_name, context)
