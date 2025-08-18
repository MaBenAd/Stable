// Global App JS (no jQuery)

(function() {
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

    function onReady() {
        const sidebar = document.getElementById('sidebar');
        const toggleSidebarBtn = document.getElementById('toggle-sidebar');
        const closeSidebarBtn = document.getElementById('close-sidebar');

        if (toggleSidebarBtn) {
            toggleSidebarBtn.addEventListener('click', function() {
                sidebar && sidebar.classList.toggle('transform');
                sidebar && sidebar.classList.toggle('-translate-x-full');
            });
        }

        if (closeSidebarBtn) {
            closeSidebarBtn.addEventListener('click', function() {
                sidebar && sidebar.classList.add('transform');
                sidebar && sidebar.classList.add('-translate-x-full');
            });
        }

        // Handle delete conversation via POST
        document.querySelectorAll('.delete-conversation').forEach(function(btn) {
            btn.addEventListener('click', function(event) {
                event.preventDefault();
                event.stopPropagation();

                const conversationId = btn.getAttribute('data-conversation-id');
                if (!conversationId) return;

                if (!confirm("Êtes-vous sûr de vouloir supprimer cette conversation ?")) {
                    return;
                }

                fetch(`/delete-conversation/${conversationId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                })
                .then(function(response) { return response.json(); })
                .then(function(data) {
                    if (data && data.success) {
                        // Remove item from UI
                        const item = btn.closest('.conversation-item');
                        if (item) item.remove();

                        // If we are currently on this conversation page, redirect home
                        const currentPath = window.location.pathname;
                        if (currentPath === `/conversation/${conversationId}/`) {
                            window.location.href = '/';
                        }
                    } else {
                        alert('Suppression impossible.');
                    }
                })
                .catch(function() { alert('Erreur réseau lors de la suppression.'); });
            });
        });

        // Highlight active conversation link
        const currentPath = window.location.pathname.replace(/\/$/, '');
        document.querySelectorAll('.conversation-item a').forEach(function(link) {
            const linkPath = link.getAttribute('href').replace(/\/$/, '');
            if (linkPath && linkPath === currentPath) {
                link.classList.add('bg-white/10');
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', onReady);
    } else {
        onReady();
    }
})();


