"""API tests for video listing, detail, genre grouping, and featured endpoints."""

from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from .models import Genre, Video


User = get_user_model()


class VideoApiTest(TestCase):
	"""Ensure authenticated users can read video endpoints."""

	def setUp(self):
		self.client = APIClient()
		self.user = User.objects.create_user(email='viewer@example.com', password='Test1234!', is_active=True)
		self.client.force_authenticate(user=self.user)

		self.genre = Genre.objects.create(name='Action', slug='action')
		self.video = Video.objects.create(
			title='Test Video',
			description='Desc',
			genre=self.genre,
			is_featured=True,
		)

	def test_list_videos(self):
		response = self.client.get('/api/videos/')
		self.assertEqual(response.status_code, 200)
		self.assertGreaterEqual(len(response.json()), 1)
		self.assertEqual(response.json()[0]['title'], self.video.title)

	def test_detail_video(self):
		response = self.client.get(f'/api/videos/{self.video.id}/')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()['id'], self.video.id)

	def test_videos_by_genre(self):
		response = self.client.get('/api/videos/by_genre/')
		self.assertEqual(response.status_code, 200)
		body = response.json()
		self.assertIn(self.genre.name, body)
		self.assertEqual(body[self.genre.name]['videos'][0]['title'], self.video.title)

	def test_featured_video(self):
		response = self.client.get('/api/videos/featured/')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()['id'], self.video.id)
