// Conversation page JS (no jQuery, XSS-safe rendering)

(function() {
    const context = window.CONVERSATION_CONTEXT || {};

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function createTextNodeWithLineBreaks(text) {
        const fragment = document.createDocumentFragment();
        const parts = (text || '').split('\n');
        parts.forEach(function(part, idx) {
            fragment.appendChild(document.createTextNode(part));
            if (idx < parts.length - 1) {
                fragment.appendChild(document.createElement('br'));
            }
        });
        return fragment;
    }

    function addMessageToChat(role, content, createdAt) {
        const messagesContainer = document.getElementById('messages-container');
        const messageDiv = document.createElement('div');
        const isUser = role === 'user';
        const time = new Date(createdAt).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });

        messageDiv.className = 'message-bubble ' + (isUser ? 'ml-auto' : 'mr-auto') + ' max-w-4xl';

        const outerFlex = document.createElement('div');
        outerFlex.className = 'flex ' + (isUser ? 'justify-end' : 'justify-start');

        const bubble = document.createElement('div');
        bubble.className = (isUser ? 'bg-blue-600 text-white' : 'bg-white text-gray-800 border border-gray-200') + ' rounded-2xl px-6 py-4 shadow-sm';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'prose prose-sm max-w-none';
        contentDiv.appendChild(createTextNodeWithLineBreaks(content));

        const timeDiv = document.createElement('div');
        timeDiv.className = 'text-xs ' + (isUser ? 'text-blue-100' : 'text-gray-500') + ' mt-2';
        timeDiv.appendChild(document.createTextNode(time));

        bubble.appendChild(contentDiv);
        bubble.appendChild(timeDiv);
        outerFlex.appendChild(bubble);
        messageDiv.appendChild(outerFlex);
        messagesContainer.appendChild(messageDiv);
    }

    function scrollToBottom(force) {
        const messagesContainer = document.getElementById('messages-container');
        const nearBottom = messagesContainer.scrollHeight - messagesContainer.scrollTop - messagesContainer.clientHeight < 120;
        if (force || nearBottom) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }

    function setTypingIndicator(visible) {
        const indicator = document.getElementById('typing-indicator');
        if (!indicator) return;
        indicator.classList.toggle('hidden', !visible);
    }

    function onReady() {
        const messageInput = document.getElementById('message-input');
        const charCount = document.getElementById('char-count');
        const form = document.getElementById('message-form');
        const submitBtn = form ? form.querySelector('button[type="submit"]') : null;

        if (messageInput) {
            const updateCounter = function() {
                if (charCount) charCount.textContent = messageInput.value.length + '/1000';
            };
            messageInput.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = Math.min(this.scrollHeight, 200) + 'px';
                updateCounter();
            });
            updateCounter();
        }

        if (form) {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                const message = (messageInput && messageInput.value || '').trim();
                if (!message) return;

                setTypingIndicator(true);
                if (submitBtn) {
                    submitBtn.disabled = true;
                }

                fetch(context.sendMessageUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        conversation_id: context.conversationId,
                        message: message
                    })
                })
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    if (data && data.success) {
                        addMessageToChat('user', data.user_message.content, data.user_message.created_at);
                        addMessageToChat('assistant', data.assistant_message.content, data.assistant_message.created_at);
                        // If images were generated, append small previews
                        if (Array.isArray(data.assistant_images)) {
                            data.assistant_images.forEach(function(img) {
                                const messagesContainer = document.getElementById('messages-container');
                                const wrap = document.createElement('div');
                                wrap.className = 'message-bubble mr-auto max-w-4xl';

                                const outer = document.createElement('div');
                                outer.className = 'flex justify-start';

                                const card = document.createElement('div');
                                card.className = 'bg-white text-gray-800 border border-gray-200 rounded-2xl px-6 py-4 shadow-sm';

                                const imgWrap = document.createElement('div');
                                imgWrap.className = 'mt-2';

                                const imageEl = document.createElement('img');
                                imageEl.className = 'generated-image w-full rounded-lg shadow-sm cursor-pointer hover:shadow-md transition-shadow';
                                imageEl.setAttribute('src', img.url);
                                imageEl.setAttribute('alt', 'Image générée');
                                imageEl.setAttribute('loading', 'lazy');
                                imageEl.dataset.imageUrl = img.url;
                                imageEl.dataset.imagePrompt = img.prompt || '';
                                imgWrap.appendChild(imageEl);

                                const promptDiv = document.createElement('div');
                                promptDiv.className = 'mt-2 text-xs text-gray-500';
                                const strong = document.createElement('strong');
                                strong.appendChild(document.createTextNode('Prompt:'));
                                promptDiv.appendChild(strong);
                                promptDiv.appendChild(document.createTextNode(' ' + (img.prompt || '')));

                                const actions = document.createElement('div');
                                actions.className = 'mt-2 text-right';
                                const downloadBtn = document.createElement('button');
                                downloadBtn.className = 'download-image-btn text-blue-600 hover:text-blue-800 text-sm';
                                downloadBtn.setAttribute('data-image-id', String(img.id));
                                const icon = document.createElement('i');
                                icon.className = 'fas fa-download mr-1';
                                downloadBtn.appendChild(icon);
                                downloadBtn.appendChild(document.createTextNode('Télécharger'));
                                actions.appendChild(downloadBtn);

                                card.appendChild(imgWrap);
                                card.appendChild(promptDiv);
                                card.appendChild(actions);
                                outer.appendChild(card);
                                wrap.appendChild(outer);
                                messagesContainer.appendChild(wrap);
                            });
                        }
                        if (data.conversation_id && data.conversation_id !== context.conversationId) {
                            context.conversationId = data.conversation_id;
                            window.history.pushState({}, '', '/conversation/' + data.conversation_id + '/');
                        }
                        // Update page title if provided
                        if (data.conversation_title) {
                            const titleEl = document.getElementById('page-title');
                            if (titleEl) titleEl.textContent = data.conversation_title;
                        }
                        scrollToBottom(true);
                    } else {
                        alert('Erreur: ' + (data && data.error ? data.error : 'inconnue'));
                    }
                })
                .catch(function() {
                    alert("Erreur lors de l'envoi du message");
                })
                .finally(function() {
                    setTypingIndicator(false);
                    if (submitBtn) submitBtn.disabled = false;
                });

                if (messageInput) {
                    messageInput.value = '';
                    messageInput.style.height = 'auto';
                    if (charCount) charCount.textContent = '0/1000';
                }
            });
        }

        // Modal behavior (accessibility)
        const modal = document.getElementById('image-modal');
        const modalContainer = document.getElementById('image-modal-container');
        const modalClose = document.getElementById('modal-close');
        const modalImage = document.getElementById('modal-image');
        const modalPrompt = document.getElementById('modal-prompt');
        let lastFocusedElement = null;

        function openImageModal(imageUrl, prompt) {
            if (!modal) return;
            lastFocusedElement = document.activeElement;
            modalImage && (modalImage.src = imageUrl);
            modalPrompt && (modalPrompt.textContent = prompt || '');
            modal.classList.remove('hidden');
            modalContainer && modalContainer.focus();
        }

        function closeImageModal() {
            if (!modal) return;
            modal.classList.add('hidden');
            if (lastFocusedElement) lastFocusedElement.focus();
        }

        document.addEventListener('click', function(e) {
            // Open modal from any generated image
            const img = e.target.closest('.generated-image');
            if (img && img.dataset.imageUrl) {
                openImageModal(img.dataset.imageUrl, img.dataset.imagePrompt);
            }

            // Download action
            if (e.target.classList && e.target.classList.contains('download-image-btn')) {
                const imageId = e.target.getAttribute('data-image-id');
                if (!imageId) return;
                // Trigger file download via GET endpoint
                window.location.href = '/download-image/' + imageId + '/';
            }
        });

        if (modal) {
            modal.addEventListener('click', function(e) {
                if (e.target === modal) {
                    closeImageModal();
                }
            });
        }
        if (modalClose) {
            modalClose.addEventListener('click', closeImageModal);
        }
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') closeImageModal();
        });

        // Initial scroll to bottom
        scrollToBottom(true);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', onReady);
    } else {
        onReady();
    }
})();


