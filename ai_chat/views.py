from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.utils import timezone
from .models import Conversation, Message, GeneratedImage
from .services.stability import generate_images, StabilityAIError
from .services.translate import translate_prompt_to_target
from django.core.files.base import ContentFile
from .forms import SignUpForm
import json


@login_required
def chat_view(request):
    """Vue principale pour l'interface de chat"""
    conversations = Conversation.objects.filter(user=request.user)
    return render(request, 'ai_chat/chat.html', {
        'conversations': conversations
    })


@login_required
def conversation_view(request, conversation_id=None):
    """Vue pour afficher une conversation spécifique"""
    if conversation_id:
        conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    else:
        # Créer une nouvelle conversation
        conversation = Conversation.objects.create(
            user=request.user,
            title="Nouvelle conversation"
        )
    
    conversations = Conversation.objects.filter(user=request.user)
    messages = conversation.messages.all()
    
    return render(request, 'ai_chat/conversation.html', {
        'conversation': conversation,
        'conversations': conversations,
        'messages': messages
    })


@login_required
@require_POST
def send_message(request):
    """API pour envoyer un message et générer une réponse avec image"""
    try:
        data = json.loads(request.body)
        conversation_id = data.get('conversation_id')
        message_content = data.get('message')
        
        if not message_content:
            return JsonResponse({'error': 'Message vide'}, status=400)
        
        # Récupérer ou créer la conversation
        if conversation_id:
            conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
        else:
            conversation = Conversation.objects.create(
                user=request.user,
                title=message_content[:50] + "..." if len(message_content) > 50 else message_content
            )
        
        # Si la conversation a un titre par défaut/vidé, la renommer avec le premier prompt
        if conversation_id and (not conversation.title or conversation.title.strip() == "Nouvelle conversation"):
            conversation.title = message_content[:50] + "..." if len(message_content) > 50 else message_content
            conversation.updated_at = timezone.now()
            conversation.save(update_fields=["title", "updated_at"])

        # Créer le message utilisateur
        user_message = Message.objects.create(
            conversation=conversation,
            role='user',
            content=message_content
        )
        
        # Appeler l'API Stability AI et créer un message assistant + images
        assistant_message = Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=f"Génération en cours pour votre prompt: '{message_content}'"
        )

        images_data = []
        try:
            translated_prompt = translate_prompt_to_target(message_content)
            images_data = generate_images(translated_prompt, samples=1)
        except StabilityAIError as api_err:
            assistant_message.content = f"Erreur lors de la génération: {api_err}"
            assistant_message.save(update_fields=['content'])
        
        assistant_images = []
        for idx, (img_bytes, ext) in enumerate(images_data):
            filename = f"stability_{assistant_message.id}_{idx}.{ext or 'png'}"
            generated = GeneratedImage(
                message=assistant_message,
                prompt=message_content,
            )
            generated.image.save(filename, ContentFile(img_bytes), save=True)
            assistant_images.append({
                'id': generated.id,
                'url': generated.image.url,
                'prompt': generated.prompt,
            })

        # Toujours rafraîchir la date de mise à jour de la conversation quand un nouveau message arrive
        conversation.updated_at = timezone.now()
        conversation.save(update_fields=["updated_at"])
        
        return JsonResponse({
            'success': True,
            'conversation_id': conversation.id,
            'user_message': {
                'id': user_message.id,
                'content': user_message.content,
                'created_at': user_message.created_at.isoformat()
            },
            'assistant_message': {
                'id': assistant_message.id,
                'content': assistant_message.content,
                'created_at': assistant_message.created_at.isoformat()
            },
            'assistant_images': assistant_images,
            'conversation_title': conversation.title
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def delete_conversation(request, conversation_id):
    """Supprimer une conversation (POST uniquement)"""
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    conversation.delete()
    # Répondre en JSON pour les requêtes AJAX
    return JsonResponse({'success': True})


@login_required
def download_image(request, image_id):
    """Télécharger une image générée"""
    generated_image = get_object_or_404(GeneratedImage, id=image_id)
    image_field = generated_image.image
    if not image_field:
        return JsonResponse({'error': 'Image introuvable'}, status=404)
    # Retourner un fichier directement (sans JSON)
    from django.http import FileResponse
    file = image_field.open('rb')
    return FileResponse(file, as_attachment=True, filename=image_field.name.split('/')[-1])


def signup(request):
    """Vue d'inscription pour créer un nouveau compte"""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('ai_chat:chat')
    else:
        form = SignUpForm()
    
    return render(request, 'ai_chat/signup.html', {'form': form})


def logout_view(request):
    """Vue de déconnexion personnalisée"""
    logout(request)
    return redirect('login')
