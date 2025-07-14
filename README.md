# Sportfwd - Django Social Media Platform

A modern social media platform built with Django featuring real-time chat, event management, and user profiles.

## 🚀 Features

- **User Authentication & Profiles**: Register, login, and customize profiles
- **Social Feed**: View posts and events from other users
- **Real-time Chat**: WebSocket-powered instant messaging
- **Event Management**: Create and manage sports events (for sponsors)
- **Follow System**: Follow/unfollow users
- **Image Upload**: Profile pictures and post images
- **Responsive Design**: Mobile-friendly interface

## 📋 Prerequisites

Before running this project, make sure you have the following installed:

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **pip** - Usually comes with Python
- **Git** - [Download Git](https://git-scm.com/downloads)

## 🛠️ Installation & Setup

### Option 1: Automated Setup (Recommended)

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd Sportfwd
   ```

2. **Run the setup script**:

   ```bash
   ./setup.sh
   ```

   This script will:

   - Create a virtual environment
   - Install all required dependencies
   - Run database migrations
   - Optionally create a superuser
   - Generate requirements.txt

3. **Activate the virtual environment**:
   ```bash
   source venv/bin/activate
   ```

### Option 2: Manual Setup

1. **Create virtual environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations**:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create superuser** (optional):
   ```bash
   python manage.py createsuperuser
   ```

## 🚀 Running the Server

### Development Server (Basic)

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

### Production Server with WebSocket Support (Recommended)

```bash
./run_server.sh
```

Visit: http://127.0.0.1:8000/

**Note**: The WebSocket server is required for real-time chat functionality.

## 📱 Usage Guide

### Getting Started

1. **Register an account** at `/register/`
2. **Login** at `/login/`
3. **Customize your profile** at `/profile/`

### Core Features

#### Social Feed (`/feed/`)

- View posts and events from all users
- Like and comment on posts
- Click "View Full Profile" to visit user profiles

#### Real-time Chat (`/inbox/`)

- Send instant messages to other users
- Messages appear in real-time using WebSockets
- Press Enter to send messages quickly

#### User Profiles

- **Your Profile** (`/profile/`): Edit your profile, view your posts and events
- **Other Users** (`/profile/<username>/`): View other users' profiles, follow/unfollow them
- **Followers/Following**: Click on follower/following counts to see lists

#### Event Management (Sponsors)

- **Create Events** (`/create-event/`): Available for sponsor accounts
- **View Events** (`/event/<id>/`): See event details and respond
- **Event Responses**: Mark as "Interested" or "Attending"

## 🏗️ Project Structure

```
Sportfwd/
├── core/                    # Main Django app
│   ├── models.py           # Database models
│   ├── views.py            # View functions
│   ├── urls.py             # URL routing
│   ├── consumers.py        # WebSocket consumers
│   ├── routing.py          # WebSocket routing
│   └── templates/          # HTML templates
├── sportfwd/               # Django project settings
│   ├── settings.py         # Project configuration
│   ├── urls.py             # Main URL routing
│   └── asgi.py             # ASGI configuration
├── media/                  # User uploaded files
├── staticfiles/            # Static files
├── setup.sh               # Automated setup script
├── run_server.sh          # WebSocket server script
└── requirements.txt       # Python dependencies
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Database

The project uses SQLite by default. For production, consider using PostgreSQL or MySQL.

## 🐛 Troubleshooting

### Common Issues

1. **"Apps aren't loaded yet" error**:

   - Make sure to use the `run_server.sh` script for WebSocket support
   - Or set `DJANGO_SETTINGS_MODULE=sportfwd.settings` before running Daphne

2. **WebSocket connection failed**:

   - Ensure you're using the WebSocket server (`./run_server.sh`)
   - Check that Daphne is installed: `pip install daphne`

3. **Static files not loading**:

   - Run: `python manage.py collectstatic`
   - Ensure `STATIC_URL` is configured in settings

4. **Migration errors**:
   - Delete `db.sqlite3` and run migrations again
   - Or run: `python manage.py migrate --run-syncdb`

### Virtual Environment Issues

```bash
# If virtual environment activation fails
source venv/bin/activate

# If packages are missing
pip install -r requirements.txt

# If you need to recreate the environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📚 API Endpoints

### Authentication

- `POST /register/` - User registration
- `POST /login/` - User login
- `GET /logout/` - User logout

### Profiles

- `GET /profile/` - Current user's profile
- `GET /profile/<username>/` - Other user's profile
- `POST /follow/<username>/` - Follow/unfollow user

### Social Features

- `GET /feed/` - Social feed
- `POST /create-post/` - Create new post
- `POST /like/<post_id>/` - Like/unlike post
- `POST /comment/<post_id>/` - Comment on post

### Chat

- `GET /inbox/` - Chat interface
- WebSocket: `/ws/chat/<room_name>/` - Real-time messaging

### Events

- `GET /create-event/` - Event creation form
- `POST /create-event/` - Create new event
- `GET /event/<event_id>/` - Event details
- `POST /event/<event_id>/respond/` - Respond to event

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

If you encounter any issues:

1. Check the troubleshooting section above
2. Review the Django documentation
3. Create an issue in the repository

---

**Happy coding! 🎉**
