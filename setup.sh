#!/bin/bash

# Sportfwd Django Project Setup Script
# This script creates a virtual environment and installs all required dependencies

echo "🚀 Setting up Sportfwd Django Project Environment..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install Django and core dependencies
echo "📚 Installing Django and core dependencies..."
pip install Django==4.2.7

# Install Channels for WebSocket support
echo "🔌 Installing Django Channels for WebSocket support..."
pip install channels==4.0.0
pip install daphne==4.0.0

# Install additional dependencies that might be needed
echo "📦 Installing additional dependencies..."
pip install Pillow==10.0.1  # For image handling
pip install python-decouple==3.8  # For environment variables

# Create requirements.txt
echo "📝 Creating requirements.txt..."
pip freeze > requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "🔐 Creating .env file..."
    cat > .env << EOF
DEBUG=True
SECRET_KEY=your-secret-key-here-change-this-in-production
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
EOF
fi

# Run Django migrations
echo "🗄️ Running Django migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
echo ""
echo "👤 Would you like to create a superuser? (y/n)"
read -r create_superuser
if [[ $create_superuser =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the development server: python manage.py runserver"
echo "3. For WebSocket support, use the run_server.sh script"
echo ""
echo "🔧 To activate the environment in the future:"
echo "   source venv/bin/activate"
echo ""
echo "🚀 To run the server with WebSocket support:"
echo "   ./run_server.sh"
echo ""
echo "📚 To install additional packages:"
echo "   pip install package_name"
echo "   pip freeze > requirements.txt" 
