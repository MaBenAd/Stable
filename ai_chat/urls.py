from django.urls import path
from . import views

app_name = 'ai_chat'

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('conversation/', views.conversation_view, name='new_conversation'),
    path('conversation/<int:conversation_id>/', views.conversation_view, name='conversation'),
    path('send-message/', views.send_message, name='send_message'),
    path('delete-conversation/<int:conversation_id>/', views.delete_conversation, name='delete_conversation'),
    path('download-image/<int:image_id>/', views.download_image, name='download_image'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),
]
