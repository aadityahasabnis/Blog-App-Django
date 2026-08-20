import json

from django.test import TestCase

from .models import Author, Post

# Create your tests here.
class PostCreateTests(TestCase):
	def setUp(self):
		self.author = Author.objects.create(name="Aadi", email="aadi@example.com")

	def test_creates_post(self):
		response = self.client.post(
			"/blogs/create/",
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


class PostDetailMutationTests(TestCase):
	def setUp(self):
		self.author = Author.objects.create(name="Aadi", email="aadi@example.com")
		self.other_author = Author.objects.create(name="Sam", email="sam@example.com")
		self.post = Post.objects.create(
			title="Original title",
			content="Original content",
			author=self.author,
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
			"/blogs/create/",
			data="not json",
			content_type="application/json",
		)

		self.assertEqual(response.status_code, 400)

	def test_rejects_unknown_author(self):
		response = self.client.post(
			"/blogs/create/",
			data=json.dumps(
				{"title": "A new post", "content": "Post content", "author_id": 999}
			),
			content_type="application/json",
		)

		self.assertEqual(response.status_code, 404)

	def test_can_create_without_csrf_token(self):
		client = self.client_class(enforce_csrf_checks=True)
		response = client.post(
			"/blogs/create/",
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
