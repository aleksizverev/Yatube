from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(request):
    post_list = Post.objects.order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "index.html", {"page": page, "paginator": paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.order_by("-pub_date")[:10]
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request, "group.html", {"group": group,
                                "page": page, "paginator": paginator}
    )


@login_required
def new_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            _new_post = form.save(commit=False)
            _new_post.author = request.user
            _new_post.save()
            return redirect("index")
        return render(request, "new_post.html", {"form": form})

    form = PostForm()
    return render(request, "new_post.html", {"form": form})


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    profile_posts = profile.posts.order_by("-pub_date")
    paginator = Paginator(profile_posts, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    follow_status = None
    if request.user.username:
        follow_status = Follow.objects.filter(
            user=request.user, author=profile)

    return render(
        request,
        "profile.html",
        {
            "page": page,
            "profile": profile,
            "paginator": paginator,
            "following": follow_status,
        },
    )


def post_view(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    profile_post = get_object_or_404(Post, author=profile, pk=post_id)
    comments = profile_post.comment_on_post.order_by("-created")
    return render(
        request,
        "post_view.html",
        {
            "profile": profile,
            "profile_post": profile_post,
            "post_comments": comments,
            "form": CommentForm(),
        },
    )


@login_required
def post_edit(request, username, post_id):
    profile_name = get_object_or_404(User, username=username)
    post_to_edit = get_object_or_404(Post, author=profile_name, pk=post_id)

    if post_to_edit.author != request.user:
        return redirect("post_view", username=username, post_id=post_id)

    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post_to_edit
    )

    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("post_view", username=username, post_id=post_id)

    return render(
        request,
        "new_post.html",
        {"form": form, "post_to_edit": post_to_edit, "is_edit": True},
    )


@login_required
def add_comment(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    commented_post = get_object_or_404(Post, author=profile, pk=post_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            _comment = form.save(commit=False)
            _comment.author = request.user
            _comment.post_id = commented_post.pk
            _comment.save()
            return redirect("post_view", username=username, post_id=post_id)
        return render(
            request,
            "post_view.html",
            {"profile_post": commented_post, "profile": profile, "form": form},
        )

    form = CommentForm()
    return render(
        request,
        "post_view.html",
        {"profile_post": commented_post, "profile": profile, "form": form},
    )


@login_required
def follow_index(request):
    authors = request.user.follower.all().values("author")
    post_list = Post.objects.filter(author__in=authors).order_by("-pub_date")
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {"page": page, "paginator": paginator})


@login_required
def profile_follow(request, username):
    profile_to_follow = get_object_or_404(User, username=username)
    follow_check = Follow.objects.filter(
        user=request.user, author=profile_to_follow).exists()
    if follow_check:
        return redirect("profile", username=username)
    else:
        if request.user != profile_to_follow:
            Follow.objects.create(user=request.user, author=profile_to_follow)
    return redirect("profile", username=username)


@login_required
def profile_unfollow(request, username):
    profile_to_unfollow = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user).filter(
        author=profile_to_unfollow).delete()
    return redirect("profile", username=username)


def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)
