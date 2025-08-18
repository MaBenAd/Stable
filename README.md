# Stable Diffusion AI Chat

A Django-based web application that provides an AI-powered chat interface with image generation capabilities using Stability AI's API. Users can have conversations and generate images from text prompts with automatic language translation support.

## Features

- 🤖 **AI Chat Interface**: Interactive chat system with conversation management
- 🎨 **Image Generation**: Generate images from text prompts using Stability AI's Stable Diffusion
- 🌐 **Multi-language Support**: Automatic prompt translation using deep-translator
- 👥 **User Authentication**: Complete user registration and login system
- 💬 **Conversation Management**: Save and manage multiple chat conversations
- 📱 **Responsive Design**: Mobile-friendly interface
- 🖼️ **Image Gallery**: View and manage generated images
- ⚙️ **Configurable Settings**: Customizable AI generation parameters

## Tech Stack

- **Backend**: Django 5.2.4
- **Database**: SQLite (default) / PostgreSQL (production ready)
- **Frontend**: HTML, CSS, JavaScript
- **Image Processing**: Pillow
- **AI Services**: Stability AI API
- **Translation**: deep-translator
- **Environment Management**: python-dotenv

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Stability AI API key

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/MaBenAd/Stable.git
   cd stable
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the root directory:
   ```env
   # Required
   STABILITY_API_KEY=your_stability_ai_api_key_here
   
   # Optional - API Configuration
   STABILITY_API_URL=https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image
   STABILITY_ENGINE=stable-diffusion-xl-1024-v1-0
   STABILITY_FALLBACK_ENGINE=stable-diffusion-xl-1024-v1-0
   
   # Optional - Generation Parameters
   STABILITY_CFG_SCALE=7
   STABILITY_STEPS=30
   STABILITY_WIDTH=1024
   STABILITY_HEIGHT=1024
   
   # Optional - Translation Settings
   TRANSLATE_PROMPTS=true
   TRANSLATE_TARGET_LANG=en
   
   # Django Settings (for production)
   DEBUG=False
   SECRET_KEY=your_secret_key_here
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

5. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create Superuser (Optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

The application will be available at `http://localhost:8000`

## Configuration

### Stability AI Setup

1. Sign up at [Stability AI](https://platform.stability.ai/)
2. Generate an API key from your dashboard
3. Add the API key to your `.env` file

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `STABILITY_API_KEY` | Your Stability AI API key | Required |
| `STABILITY_API_URL` | Stability AI API endpoint | https://api.stability.ai/v1/generation/... |
| `STABILITY_ENGINE` | AI model to use | stable-diffusion-xl-1024-v1-0 |
| `STABILITY_CFG_SCALE` | Guidance scale (1-35) | 7 |
| `STABILITY_STEPS` | Generation steps (10-150) | 30 |
| `STABILITY_WIDTH` | Image width in pixels | 1024 |
| `STABILITY_HEIGHT` | Image height in pixels | 1024 |
| `TRANSLATE_PROMPTS` | Enable prompt translation | true |
| `TRANSLATE_TARGET_LANG` | Target language for translation | en |

## Usage

### Basic Chat

1. Register a new account or login
2. Start a new conversation
3. Type your message and press Enter
4. The AI will respond to your queries

### Image Generation

1. In a chat conversation, type a descriptive prompt
2. The system will generate an image based on your prompt
3. Images are saved and displayed in the chat
4. View all generated images in your conversation history

### Conversation Management

- **New Conversation**: Click "New Chat" to start fresh
- **Save Conversations**: All chats are automatically saved
- **View History**: Access previous conversations from the sidebar
- **Delete Conversations**: Remove unwanted chat histories

## API Endpoints

### Authentication
- `POST /accounts/register/` - User registration
- `POST /accounts/login/` - User login
- `POST /accounts/logout/` - User logout

### Chat
- `GET /` - Main chat interface
- `POST /chat/send/` - Send message
- `GET /chat/conversations/` - List user conversations
- `POST /chat/new/` - Create new conversation
- `DELETE /chat/conversation/<id>/` - Delete conversation

### Images
- `GET /media/generated_images/` - Access generated images
- `GET /chat/images/` - View image gallery

## Project Structure

```
stable/
├── ai_chat/                    # Main application
│   ├── migrations/            # Database migrations
│   ├── services/              # External service integrations
│   │   ├── stability.py      # Stability AI integration
│   │   └── translate.py      # Translation service
│   ├── models.py             # Database models
│   ├── views.py              # View controllers
│   ├── urls.py               # URL routing
│   ├── forms.py              # Django forms
│   └── admin.py              # Admin interface
├── stable/                    # Django project settings
│   ├── settings.py           # Main configuration
│   ├── urls.py               # Root URL configuration
│   └── wsgi.py               # WSGI application
├── templates/                 # HTML templates
│   ├── ai_chat/              # Chat templates
│   └── registration/         # Auth templates
├── static/                    # Static files (CSS, JS, images)
├── media/                     # User uploaded/generated files
├── requirements.txt           # Python dependencies
└── manage.py                 # Django management script
```

## Models

### Conversation
- Represents a chat conversation
- Links to User model
- Tracks creation and update times

### Message
- Individual messages within conversations
- Supports both user and assistant roles
- Can include generated images

### GeneratedImage
- Stores AI-generated images
- Links to specific messages
- Includes original prompt

## Development

### Running Tests
```bash
python manage.py test
```

### Collecting Static Files
```bash
python manage.py collectstatic
```

### Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Admin Interface
Access the Django admin at `/admin/` with your superuser credentials.

## Deployment

### Production Settings

1. **Update settings for production**:
   - Set `DEBUG = False`
   - Configure `ALLOWED_HOSTS`
   - Use environment variables for secrets

2. **Database Configuration**:
   ```python
   # For PostgreSQL
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'your_db_name',
           'USER': 'your_db_user',
           'PASSWORD': 'your_db_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

3. **Static Files**:
   ```bash
   python manage.py collectstatic --noinput
   ```

4. **Security Checklist**:
   - Use HTTPS
   - Set strong SECRET_KEY
   - Configure CSRF settings
   - Set up proper CORS headers
   - Use secure session cookies

### Deployment Platforms

- **Heroku**: Use `Procfile` and `runtime.txt`
- **AWS**: Configure with Elastic Beanstalk or EC2
- **Docker**: Create Dockerfile for containerization
- **PythonAnywhere**: Follow their Django deployment guide

## Troubleshooting

### Common Issues

1. **Stability AI API Errors**
   - Check API key validity
   - Verify account credits
   - Ensure proper internet connection

2. **Image Upload Issues**
   - Check media directory permissions
   - Verify MEDIA_ROOT configuration
   - Ensure sufficient disk space

3. **Translation Errors**
   - Check internet connection
   - Verify translation service availability
   - Review language code format

4. **Database Issues**
   - Run migrations: `python manage.py migrate`
   - Check database permissions
   - Verify database connection settings

### Debug Mode

Enable debug mode in development by setting `DEBUG = True` in settings.py or your `.env` file.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the troubleshooting section

## Acknowledgments

- [Stability AI](https://stability.ai/) for image generation API
- [Django](https://www.djangoproject.com/) for the web framework
- [deep-translator](https://github.com/nidhaloff/deep-translator) for translation services

---

**Note**: This application requires an active Stability AI API key to function properly. Make sure to follow their terms of service and usage guidelines.
