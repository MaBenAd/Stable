from django.contrib import admin
from .models import Conversation, Message, GeneratedImage


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'created_at', 'updated_at', 'message_count']
    list_filter = ['created_at', 'updated_at', 'user']
    search_fields = ['title', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Nombre de messages'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['role', 'content_preview', 'conversation', 'created_at']
    list_filter = ['role', 'created_at', 'conversation__user']
    search_fields = ['content', 'conversation__title']
    readonly_fields = ['created_at']
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Contenu'


@admin.register(GeneratedImage)
class GeneratedImageAdmin(admin.ModelAdmin):
    list_display = ['prompt_preview', 'message', 'created_at']
    list_filter = ['created_at', 'message__conversation__user']
    search_fields = ['prompt', 'message__content']
    readonly_fields = ['created_at']
    
    def prompt_preview(self, obj):
        return obj.prompt[:50] + '...' if len(obj.prompt) > 50 else obj.prompt
    prompt_preview.short_description = 'Prompt'
