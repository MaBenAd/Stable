import json
import os
import tempfile
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from .models import Conversation, Message, GeneratedImage


class ChatViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='tester', email='t@example.com', password='pass12345')

    def login(self):
        self.client.login(username='tester', password='pass12345')

    def test_login_required_redirects(self):
        resp = self.client.get(reverse('ai_chat:chat'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/accounts/login/', resp.url)

    def test_conversation_creation_via_get(self):
        self.login()
        resp = self.client.get(reverse('ai_chat:new_conversation'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Conversation.objects.filter(user=self.user).count(), 1)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    @patch('ai_chat.views.translate_prompt_to_target', side_effect=lambda x: x)
    @patch('ai_chat.views.generate_images')
    def test_send_message_creates_conversation_messages_and_image(self, mock_gen, _mock_translate):
        self.login()
        mock_gen.return_value = [(b'fakeimagedata', 'png')]
        payload = {
            'message': 'Un chat mignon avec un chapeau bleu',
        }
        resp = self.client.post(reverse('ai_chat:send_message'), data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 200, msg=f"Unexpected status: {resp.status_code}, body={resp.content}")
        data = resp.json()
        self.assertTrue(data.get('success'), msg=f"Response not success: {data}")
        self.assertIn('conversation_id', data, msg=f"Missing conversation_id: {data}")
        self.assertIn('assistant_message', data, msg=f"Missing assistant_message: {data}")
        self.assertIn('assistant_images', data, msg=f"Missing assistant_images: {data}")
        self.assertEqual(len(data['assistant_images']), 1, msg=f"Images not returned as expected: {data}")

        conv = Conversation.objects.get(id=data['conversation_id'])
        self.assertEqual(conv.user, self.user)
        self.assertTrue(Message.objects.filter(conversation=conv, role='user').exists())
        self.assertTrue(Message.objects.filter(conversation=conv, role='assistant').exists())
        self.assertTrue(GeneratedImage.objects.filter(message__conversation=conv).exists())

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    @patch('ai_chat.views.translate_prompt_to_target', side_effect=lambda x: x)
    @patch('ai_chat.views.generate_images')
    def test_conversation_title_from_first_prompt(self, mock_gen, _mock_translate):
        self.login()
        mock_gen.return_value = []
        first_prompt = 'Première idée de prompt pour nommer la conversation'
        resp = self.client.post(reverse('ai_chat:send_message'), data=json.dumps({'message': first_prompt}), content_type='application/json')
        self.assertEqual(resp.status_code, 200, msg=f"Unexpected status: {resp.status_code}, body={resp.content}")
        conv_id = resp.json()['conversation_id']
        conv = Conversation.objects.get(id=conv_id)
        self.assertTrue(conv.title.startswith('Première idée'), msg=f"Title not set from first prompt: '{conv.title}'")

    def test_send_message_empty_returns_400(self):
        self.login()
        resp = self.client.post(reverse('ai_chat:send_message'), data=json.dumps({'message': ''}), content_type='application/json')
        self.assertEqual(resp.status_code, 400, msg=f"Expected 400 for empty message, got {resp.status_code}")

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_delete_conversation_removes_files(self):
        self.login()
        conv = Conversation.objects.create(user=self.user, title='Temp')
        msg = Message.objects.create(conversation=conv, role='assistant', content='image')
        gen = GeneratedImage(message=msg, prompt='x')
        gen.image.save('test_img.png', ContentFile(b'123'), save=True)
        file_path = gen.image.path
        self.assertTrue(os.path.exists(file_path))

        resp = self.client.post(reverse('ai_chat:delete_conversation', args=[conv.id]))
        self.assertEqual(resp.status_code, 200, msg=f"Delete conversation failed: {resp.status_code}")
        self.assertFalse(Conversation.objects.filter(id=conv.id).exists())
        # Signal should have deleted the file on disk
        self.assertFalse(os.path.exists(file_path))

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_download_image(self):
        self.login()
        conv = Conversation.objects.create(user=self.user, title='Temp')
        msg = Message.objects.create(conversation=conv, role='assistant', content='image')
        gen = GeneratedImage(message=msg, prompt='x')
        gen.image.save('test_img2.png', ContentFile(b'abc'), save=True)

        resp = self.client.get(reverse('ai_chat:download_image', args=[gen.id]))
        self.assertEqual(resp.status_code, 200, msg=f"Download failed: {resp.status_code}")
        self.assertIn('attachment', resp.get('Content-Disposition', ''))

    def test_signup_creates_user(self):
        resp = self.client.get(reverse('ai_chat:signup'))
        self.assertEqual(resp.status_code, 200)
        post = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'StrongPassw0rd!',
            'password2': 'StrongPassw0rd!'
        }
        resp2 = self.client.post(reverse('ai_chat:signup'), data=post)
        # Should redirect to chat after signup
        self.assertEqual(resp2.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

