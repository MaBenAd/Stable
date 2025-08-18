from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Conversation(models.Model):
    """Modèle pour représenter une conversation de chat"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.title or 'Conversation'} - {self.user.username}"


class Message(models.Model):
    """Modèle pour représenter un message dans une conversation"""
    ROLE_CHOICES = [
        ('user', 'Utilisateur'),
        ('assistant', 'Assistant'),
    ]
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    image = models.ImageField(upload_to='generated_images/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.role} - {self.content[:50]}..."


class GeneratedImage(models.Model):
    """Modèle pour stocker les images générées par l'IA"""
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='generated_images')
    image = models.ImageField(upload_to='generated_images/')
    prompt = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Image générée - {self.prompt[:50]}..."
