from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .models import Comment, Follow, Group, Post, User

DUMMY_CACHE = {"default": {
    "BACKEND": "django.core.cache.backends.dummy.DummyCache"}}


class TestPostAppearance(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            username="prikol", email="prikol@haha.ru", password=12345
        )
        self.client.force_login(self.user)
        self.text_in_post = "Test post text!"

    @override_settings(CACHES=DUMMY_CACHE)
    def test_post_appearance(self):
        self.client.post(reverse("new_post"), {"text": self.text_in_post})
        response_profile = self.client.get(
            reverse("profile", kwargs={"username": self.user.username})
        )
        self.assertContains(response_profile, text=self.text_in_post)

        response_index = self.client.get(reverse("index"))
        self.assertContains(response_index, text=self.text_in_post)

        response_post = self.client.get(
            reverse(
                "post_view",
                kwargs={
                    "username": self.user.username,
                    "post_id": Post.objects.get(author=self.user).pk,
                },
            )
        )
        self.assertContains(response_post, text=self.text_in_post)


class TestPostEdit(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            username="prikol", email="prikol@haha.ru", password=12345
        )
        self.text_in_post = "Test edit post!"
        self.text_in_edited_post = "This post was edited!"
        self.post_to_edit = Post.objects.create(
            text=self.text_in_post, author=self.user
        )
        self.client.force_login(self.user)

    @override_settings(CACHES=DUMMY_CACHE)
    def test_post_edit_check(self):
        self.client.post(
            reverse(
                "post_edit",
                kwargs={"username": self.user,
                        "post_id": self.post_to_edit.pk},
            ),
            {"text": self.text_in_edited_post},
        )
        response_profile = self.client.get(
            reverse("profile", kwargs={"username": self.user.username})
        )
        self.assertContains(response_profile, text=self.text_in_edited_post)

        response_index = self.client.get(reverse("index"))
        self.assertContains(response_index, text=self.text_in_edited_post)

        response_post = self.client.get(
            reverse(
                "post_view",
                kwargs={
                    "username": self.user.username,
                    "post_id": Post.objects.get(author=self.user).pk,
                },
            )
        )
        self.assertContains(response_post, text=self.text_in_edited_post)


class TestNewPost(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            username="prikol", email="prikol@haha.ru", password=12345
        )
        self.client.force_login(self.user)
        self.text_in_post = "Test post text!"

    def test_user_post_creation(self):
        response = self.client.post(
            reverse("new_post"), {"text": self.text_in_post})
        self.assertRedirects(response, reverse("index"))
        self.assertEqual(Post.objects.count(), 1)
        self.assertTrue(
            Post.objects.filter(text=self.text_in_post)
            .filter(author=self.user)
            .exists()
        )

    def test_not_auth_user_post_creation(self):
        self.client.logout()
        response = self.client.get(reverse("new_post"), follow=True)
        self.assertRedirects(response, "/auth/login/?next=/new/")
        self.assertEqual(Post.objects.count(), 0)


class TestHandlerErrors(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_name = "kokosik"

    def test_404_error(self):
        response = self.client.get(
            reverse("profile", kwargs={"username": self.test_name})
        )
        self.assertEqual((response.status_code), 404)


class TestCheckImgTegAppearance(TestCase):
    def setUp(self):
        self.client = Client()
        self.text_in_post = "Test edit post!"
        self.text_in_edited_post = "This post was edited!"
        self.group_slug = "nice"
        self.group_title = "nice group"
        self.group = Group.objects.create(
            title=self.group_title, slug=self.group_slug)
        self.tag = 'img class="card-img"'
        self.user = User.objects.create(
            username="prikol", email="prikol@haha.ru", password="SmAk1234"
        )
        self.post_to_edit = Post.objects.create(
            text=self.text_in_post, author=self.user, group=self.group
        )
        self.client.force_login(self.user)

    def test_post_view_have_img_tag(self):
        with open("C:/Dev/hw04_tests/test_files/file.png", "rb") as img:
            response = self.client.post(
                reverse(
                    "post_edit",
                    kwargs={"username": self.user,
                            "post_id": self.post_to_edit.pk},
                ),
                {"text": self.text_in_edited_post, "image": img},
                follow=True,
            )
        self.assertContains(response, self.tag)

    @override_settings(CACHES=DUMMY_CACHE)
    def test_group_view_have_img_tag(self):
        with open("C:/Dev/hw04_tests/test_files/file.png", "rb") as img:
            response = self.client.post(
                reverse(
                    "post_edit",
                    kwargs={"username": self.user,
                            "post_id": self.post_to_edit.pk},
                ),
                {
                    "text": self.text_in_edited_post,
                    "group": self.group.pk,
                    "image": img,
                },
                follow=True,
            )

            response_group = self.client.get(
                reverse("group_posts", kwargs={"slug": self.group_slug})
            )
            self.assertContains(response_group, self.tag)

            response_profile = self.client.get(
                reverse("profile", kwargs={"username": self.user})
            )
            self.assertContains(response_profile, self.tag)

            response_index = self.client.get(reverse("index"))
            self.assertContains(response_index, self.tag)


class TestUngraphicalUploadProtection(TestCase):
    def setUp(self):
        self.client = Client()
        self.text_in_post = "Test edit post!"
        self.text_in_edited_post = "This post was edited!"
        self.tag = 'img class="card-img"'
        self.user = User.objects.create(
            username="prikol", email="prikol@haha.ru", password="SmAk1234"
        )
        self.post_to_edit = Post.objects.create(
            text=self.text_in_post, author=self.user
        )
        self.client.force_login(self.user)

    def test_ungraphical_upload_protection(self):
        with open("C:/Dev/hw04_tests/test_files/text_file.txt", "rb") as img:
            response = self.client.post(
                reverse(
                    "post_edit",
                    kwargs={"username": self.user,
                            "post_id": self.post_to_edit.pk},
                ),
                {"text": self.text_in_edited_post, "image": img},
            )
            self.assertFormError(
                response,
                "form",
                "image",
                "Загрузите правильное изображение. Файл, который вы загрузили,"
                + " поврежден или не является изображением.",
            )


class TestCache(TestCase):
    def setUp(self):
        self.client = Client()
        self.text_in_post = "Test edit post!"
        self.text_in_edited_post = "This post was edited!"
        self.user = User.objects.create(
            username="prikol", email="prikol@haha.ru", password="SmAk1234"
        )
        self.post_for_cache = Post.objects.create(
            text=self.text_in_post, author=self.user
        )
        self.client.force_login(self.user)

    def test_cache_work_on_index(self):
        response = self.client.get(reverse("index"))
        self.assertContains(response, self.text_in_post)
        self.client.post(
            reverse(
                "post_edit",
                kwargs={"username": self.user,
                        "post_id": self.post_for_cache.pk},
            ),
            {"text": self.text_in_edited_post},
        )
        response = self.client.get(reverse("index"))
        self.assertContains(response, self.text_in_post)


class TestUserSubscription(TestCase):
    def setUp(self):
        self.client_user = Client()
        self.client_author = Client()
        self.user = User.objects.create(
            username="prikol", email="prikol@haha.ru", password="SmAk1234"
        )
        self.author = User.objects.create(
            username="keks", email="keks@haha.ru", password="JuiceWRLD11"
        )
        self.client_user.force_login(self.user)
        self.client_author.force_login(self.author)
        self.text_in_post = "Test edit post!"

    def test_authorized_user_sub(self):
        response_sub = self.client_user.get(
            reverse("profile_follow", kwargs={"username": self.author}), follow=True
        )
        self.assertEqual(response_sub.status_code, 200)
        self.assertTrue(
            Follow.objects.filter(user=self.user, author=self.author).exists()
        )

    def test_authorized_user_unsub(self):
        Follow.objects.create(user=self.user, author=self.author)
        response_unsub = self.client_user.get(
            reverse("profile_unfollow", kwargs={"username": self.author}), follow=True
        )
        self.assertEqual(response_unsub.status_code, 200)
        self.assertFalse(
            Follow.objects.filter(user=self.user, author=self.author).exists()
        )


class TestSubUserPostAppearance(TestCase):
    def setUp(self):
        self.client_user = Client()
        self.client_author = Client()
        self.client_user2 = Client()
        self.user = User.objects.create(
            username="prikol", email="prikol@haha.ru", password="SmAk1234"
        )
        self.author = User.objects.create(
            username="keks", email="keks@haha.ru", password="JuiceWRLD11"
        )
        self.user2 = User.objects.create(
            username="peks", email="peks@haha.ru", password="JuiceWRLD11"
        )
        self.text_in_post = "Test post!"
        Post.objects.create(text=self.text_in_post, author=self.author)
        self.client_user.force_login(self.user)
        self.client_user2.force_login(self.user2)
        self.client_author.force_login(self.author)

    def test_auth_user_post_appearance(self):
        Follow.objects.create(user=self.user, author=self.author)
        response = self.client_user.get(reverse("follow_index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.text_in_post)

    def test_nonauth_user_post_appearance(self):
        response = self.client_user2.get(reverse("follow_index"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.text_in_post)


class TestUserComments(TestCase):
    def setUp(self):
        self.client_user = Client()
        self.client_author = Client()
        self.user = User.objects.create(
            username="prikol", email="prikol@haha.ru", password="SmAk1234"
        )
        self.author = User.objects.create(
            username="keks", email="keks@haha.ru", password="JuiceWRLD11"
        )
        self.client_user.force_login(self.user)
        self.client_author.force_login(self.author)
        self.text_in_post = "Test post!"
        self.text_in_comment = "Test comment"

    def test_auth_user_can_comment(self):
        self.post = Post.objects.create(
            text=self.text_in_post, author=self.author)
        response = self.client_user.post(
            reverse(
                "add_comment", kwargs={"username": self.author, "post_id": self.post.pk}
            ),
            {"text": self.text_in_comment, "author": self.user},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.comment = Comment.objects.last()
        self.assertEqual(self.comment.text, self.text_in_comment)
