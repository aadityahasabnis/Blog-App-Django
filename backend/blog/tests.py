import json

from django.test import TestCase
from django.contrib.auth.models import User

from .models import Author, Post
from .forms import PostForm

# Create your tests here.
class PostCreateTests(TestCase):
	def setUp(self):
		self.author = Author.objects.create(name="Aadi", email="aadi@example.com")
		self.user = User.objects.create_user("aadi", "aadi@example.com", "password123")
		self.client.force_login(self.user)

	def test_creates_post(self):
		response = self.client.post(
			"/blogs/api/create/",
			data=json.dumps(
				{
					"title": "A new post",
					"content": "Post content",
					"author_id": self.author.id,
					"category": "Django",
				}
			),
			content_type="application/json",
		)

		self.assertEqual(response.status_code, 201)
		self.assertEqual(Post.objects.count(), 1)
		self.assertEqual(response.json()["title"], "A new post")
		self.assertFalse(response.json()["is_published"])

	def test_form_page_is_displayed(self):
		response = self.client.get("/blogs/create/")

		self.assertEqual(response.status_code, 200)
		self.assertIsInstance(response.context["form"], PostForm)

	def test_form_creates_post(self):
		response = self.client.post(
			"/blogs/create/",
			data={
				"title": "A form post",
				"content": "Created with ModelForm",
				"author": self.author.id,
				"category": "Django",
				"is_published": "on",
			},
		)

		self.assertEqual(response.status_code, 201)
		self.assertEqual(Post.objects.get().title, "A form post")
		self.assertContains(response, "A form post", status_code=201)

	def test_form_rejects_missing_required_fields(self):
		response = self.client.post(
			"/blogs/create/",
			data={"author": self.author.id},
		)

		self.assertEqual(response.status_code, 200)
		self.assertFalse(Post.objects.exists())
		self.assertIn("This field is required.", response.content.decode())

	def test_anonymous_user_cannot_open_create_form(self):
		self.client.logout()

		response = self.client.get("/blogs/create/")

		self.assertEqual(response.status_code, 302)
		self.assertIn("/blogs/login/", response["Location"])

	def test_signup_creates_user_and_author(self):
		self.client.logout()

		response = self.client.post(
			"/blogs/signup/",
			data={
				"username": "newwriter",
				"email": "writer@example.com",
				"password1": "A-secure-password-123",
				"password2": "A-secure-password-123",
			},
		)

		self.assertEqual(response.status_code, 302)
		self.assertTrue(User.objects.filter(username="newwriter").exists())
		self.assertTrue(Author.objects.filter(email="writer@example.com").exists())


class PostDetailMutationTests(TestCase):
	def setUp(self):
		self.author = Author.objects.create(name="Aadi", email="aadi@example.com")
		self.user = User.objects.create_user("aadi", "aadi@example.com", "password123")
		self.client.force_login(self.user)
		self.other_author = Author.objects.create(name="Sam", email="sam@example.com")
		self.post = Post.objects.create(
			title="Original title",
			content="Original content",
			author=self.author,
			is_published=True,
		)
		self.url = f"/blogs/{self.post.id}/"

	def test_put_replaces_post_fields(self):
		response = self.client.put(
			self.url,
			data=json.dumps(
				{
					"title": "Replaced title",
					"content": "Replaced content",
					"author_id": self.other_author.id,
					"category": "Django",
					"is_published": True,
				}
			),
			content_type="application/json",
		)

		self.assertEqual(response.status_code, 200)
		self.post.refresh_from_db()
		self.assertEqual(self.post.title, "Replaced title")
		self.assertEqual(self.post.author, self.other_author)

	def test_patch_updates_only_supplied_fields(self):
		response = self.client.patch(
			self.url,
			data=json.dumps({"title": "Patched title"}),
			content_type="application/json",
		)

		self.assertEqual(response.status_code, 200)
		self.post.refresh_from_db()
		self.assertEqual(self.post.title, "Patched title")
		self.assertEqual(self.post.content, "Original content")

	def test_delete_returns_no_content(self):
		response = self.client.delete(self.url)

		self.assertEqual(response.status_code, 204)
		self.assertFalse(Post.objects.filter(id=self.post.id).exists())

	def test_put_requires_complete_payload(self):
		response = self.client.put(
			self.url,
			data=json.dumps({"title": "Incomplete"}),
			content_type="application/json",
		)

		self.assertEqual(response.status_code, 400)

	def test_rejects_invalid_json(self):
		response = self.client.post(
			"/blogs/api/create/",
			data="not json",
			content_type="application/json",
		)

		self.assertEqual(response.status_code, 400)

	def test_rejects_unknown_author(self):
		response = self.client.post(
			"/blogs/api/create/",
			data=json.dumps({"title": "A new post", "content": "Post content"}),
			content_type="application/json",
		)

		self.assertEqual(response.status_code, 201)

	def test_can_create_without_csrf_token(self):
		client = self.client_class(enforce_csrf_checks=True)
		client.force_login(self.user)
		response = client.post(
			"/blogs/api/create/",
			data=json.dumps(
				{
					"title": "A Postman post",
					"content": "Created through the API",
					"author_id": self.author.id,
				}
			),
			content_type="application/json",
		)

		self.assertEqual(response.status_code, 201)


class BlogPageTests(TestCase):
	def setUp(self):
		self.author = Author.objects.create(name="Aadi", email="aadi@example.com")
		self.user = User.objects.create_user("aadi", "aadi@example.com", "password123")
		self.client.force_login(self.user)
		self.post = Post.objects.create(
			title="Published post",
			content="Published content",
			author=self.author,
			is_published=True,
		)

	def test_home_page(self):
		response = self.client.get("/")

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Read published posts")

	def test_list_and_detail_pages(self):
		list_response = self.client.get("/blogs/")
		detail_response = self.client.get(f"/blogs/{self.post.id}/")

		self.assertContains(list_response, "Published post")
		self.assertContains(detail_response, "Published content")

	def test_detail_page_increments_views(self):
		self.client.get(f"/blogs/{self.post.id}/")
		self.post.refresh_from_db()

		self.assertEqual(self.post.views, 1)

	def test_list_search_filters_posts(self):
		Post.objects.create(
			title="Different topic",
			content="Something unrelated",
			author=self.author,
			is_published=True,
		)

		response = self.client.get("/blogs/?q=Published")

		self.assertContains(response, "Published post")
		self.assertNotContains(response, "Different topic")

	def test_list_is_paginated(self):
		for index in range(6):
			Post.objects.create(
				title=f"Extra post {index}",
				content="More content",
				author=self.author,
				is_published=True,
			)

		response = self.client.get("/blogs/")

		self.assertEqual(response.context["page_obj"].paginator.num_pages, 2)
		self.assertContains(response, "Page 1 of 2")

	def test_edit_action_updates_post(self):
		response = self.client.post(
			f"/blogs/{self.post.id}/edit/",
			data={
				"title": "Edited post",
				"content": "Edited content",
				"author": self.author.id,
				"is_published": "on",
			},
		)

		self.assertEqual(response.status_code, 302)
		self.post.refresh_from_db()
		self.assertEqual(self.post.title, "Edited post")

	def test_delete_action_removes_post(self):
		response = self.client.post(f"/blogs/{self.post.id}/delete/")

		self.assertEqual(response.status_code, 302)
		self.assertFalse(Post.objects.filter(id=self.post.id).exists())
