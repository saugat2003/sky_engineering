from django.contrib.auth.models import User
from django.test import TestCase

from messaging.models import Message


class MessageModelTest(TestCase):
	def setUp(self):
		self.sender = User.objects.create_user(username='sender', email='sender@example.com', password='pass')
		self.recipient = User.objects.create_user(username='recipient', email='recipient@example.com', password='pass')

	def test_message_string_representation_is_readable(self):
		message = Message.objects.create(
			sender=self.sender,
			recipient=self.recipient,
			subject='Deployment update',
			body='The release is ready.',
		)

		self.assertEqual(str(message), 'Deployment update | sender -> recipient')
