# 🎲 Enhanced Lottery Number Generator

A powerful Django web application that generates unique lottery combinations with advanced features including bulk generation, Texas Lottery integration, and modern responsive UI.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Django](https://img.shields.io/badge/Django-5.2-green.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Enhanced Features

### 🎯 **Bulk Generation with Multiple First Numbers**
- Generate combinations using multiple seed numbers (e.g., 1, 3, 5)
- Perfect for Powerball and Mega Millions strategies
- Organized results grouped by first number used
- Export bulk results with detailed tracking

### 🌱 **Advanced Seeded Generation**
- Single seed generation (start with one lucky number)
- Bulk seed generation (start with multiple numbers simultaneously)
- Track which seed number was used for each combination
- Ensure all generated combinations include your chosen first numbers

### 💾 **Save & Manage Combinations**
- Save your favorite lottery combinations with custom names
- Check saved combinations against historical draws
- Bulk operations for managing multiple combinations
- Organize combinations by game type (Mega Millions/Powerball)

### 📊 **Enhanced Export Features**
- Export combinations to CSV with comprehensive details
- Filter exports by date range and game type
- Track generation method and seed numbers used
- Professional file naming with timestamps

### 🏴󠁵󠁳󠁴󠁸󠁿 **Texas Lottery Integration**
- Direct links to official Texas Lottery checking pages
- Quick access to Mega Millions and Powerball verification tools
- Latest results fetching capabilities
- Seamless integration with official lottery websites

### 🎨 **Modern Responsive UI**
- Bootstrap 5 with professional tabbed navigation
- Mobile-responsive design for all devices
- Animated lottery ball displays
- Interactive bulk selection and management tools

### 📱 **Mobile-Ready API**
- RESTful JSON endpoints for mobile app integration
- API for automated number generation
- Combination checking and validation endpoints

## 🚀 Linux Server Installation Guide

### Prerequisites

Ensure your Linux server has the following installed:

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python 3.8+ and required packages
sudo apt install python3 python3-pip python3-venv git -y

# Verify Python version (should be 3.8+)
python3 --version
```

### Step 1: Clone the Repository

```bash
# Clone the enhanced lottery generator
git clone https://github.com/tanzeelgcuf/lottery-number-generator.git

# Navigate to project directory
cd lottery-number-generator

# Verify project structure
ls -la
```

### Step 2: Create and Activate Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify virtual environment is active (should show (venv) in prompt)
which python
```

### Step 3: Install Dependencies

```bash
# Upgrade pip to latest version
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list
```

### Step 4: Database Setup

```bash
# Create database migrations
python manage.py makemigrations

# Apply migrations to create database tables
python manage.py migrate

# Verify database setup
python manage.py check
```

### Step 5: Run the Application

#### For Development (Local Testing):
```bash
# Run on localhost only
python manage.py runserver
```

#### For Production (Server Access):
```bash
# Run on all interfaces (accessible from outside)
python manage.py runserver 0.0.0.0:8000
```

#### For Custom Port:
```bash
# Run on custom port (e.g., 8080)
python manage.py runserver 0.0.0.0:8080
```

### Step 6: Access the Application

- **Local Development:** http://127.0.0.1:8000/
- **Server Access:** http://YOUR_SERVER_IP:8000/
- **Custom Port:** http://YOUR_SERVER_IP:8080/

Replace `YOUR_SERVER_IP` with your actual server IP address.

## 🎯 Usage Guide

### 1. **Generate Numbers with Multiple First Numbers**

Perfect for Powerball strategies using numbers like 1, 3, 5:

1. Visit the homepage
2. Click **"Generate Numbers"** tab
3. Use **"Bulk First Numbers"** section (rightmost card)
4. **Game Type:** Select "Powerball"
5. **First Numbers:** Enter `1, 3, 5`
6. **Sets per Number:** Choose how many combinations per first number
7. Click **"Generate Bulk Sets"**

**Result:** You'll get organized combinations grouped by first number:
- 5 combinations starting with 1
- 5 combinations starting with 3  
- 5 combinations starting with 5

### 2. **Save Your Combinations**

1. Click **"Save Numbers"** tab
2. Enter a **combination name** (e.g., "Lucky Numbers")
3. Select **game type** (Mega Millions/Powerball)
4. Enter your **5 main numbers** (comma-separated)
5. Enter your **mega/power ball number**
6. Click **"Save Combination"**

### 3. **Export Results**

1. After generating combinations
2. Click **"Export CSV"** for detailed export
3. **Advanced Export:** Use export with date filtering
4. **Bulk Export:** Select specific combinations to export

### 4. **Texas Lottery Integration**

1. Click **"Texas Lottery"** tab
2. Use **direct links** to official Texas Lottery checking pages:
   - **Mega Millions:** Direct link to official checking tool
   - **Powerball:** Direct link to official checking tool
3. **Fetch Latest Results:** Get recent winning numbers

## 🎲 Supported Games

### Mega Millions
- **Main Numbers:** 5 numbers from 1-70
- **Mega Ball:** 1 number from 1-25
- **Drawings:** Tuesday & Friday
- **Texas Lottery:** [Check Numbers](https://www.texaslottery.com/export/sites/lottery/Games/Check_Your_Numbers.html#MegaMillions)

### Powerball
- **Main Numbers:** 5 numbers from 1-69
- **Power Ball:** 1 number from 1-26
- **Drawings:** Monday, Wednesday & Saturday
- **Texas Lottery:** [Check Numbers](https://www.texaslottery.com/export/sites/lottery/Games/Check_Your_Numbers.html#Powerball)

## 📁 Project Structure

```
lottery-number-generator/
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── README.md                   # Project documentation
├── generator/                  # Main Django application
│   ├── models.py              # Database models (enhanced)
│   ├── views.py               # View functions (bulk generation)
│   ├── urls.py                # URL routing (enhanced endpoints)
│   ├── admin.py               # Admin interface
│   ├── apps.py                # App configuration
│   ├── templates/             # HTML templates
│   │   └── generator/
│   │       ├── index.html     # Enhanced homepage with tabs
│   │       ├── results.html   # Results display
│   │       ├── bulk_results.html # Bulk generation results
│   │       ├── saved_combinations.html # Saved numbers
│   │       └── check_results.html # Checking results
│   ├── migrations/            # Database migrations
│   └── management/            # Custom management commands
│       └── commands/
│           └── import_lottery_data.py
├── lottery_generator/         # Django project settings
│   ├── settings.py           # Project configuration
│   ├── urls.py              # Main URL configuration
│   ├── wsgi.py              # WSGI configuration
│   └── asgi.py              # ASGI configuration
└── venv/                    # Virtual environment (created during setup)
```

## 📱 API Endpoints

### Generate Numbers
```bash
# Random generation
GET /api/generate/?game_type=powerball&count=10

# Seeded generation
GET /api/generate/?game_type=powerball&count=5&seed_number=7

# Response format:
{
    "combinations": [
        {
            "main_numbers": [7, 15, 22, 35, 67],
            "mega_ball": 12
        }
    ],
    "game_type": "powerball",
    "seed_number": 7
}
```

### Check Numbers
```bash
POST /api/check/
Content-Type: application/json

{
    "main_numbers": [1, 15, 22, 35, 67],
    "mega_ball": 7,
    "game_type": "powerball"
}
```

## 🔧 Advanced Configuration

### For Production Deployment

1. **Create Superuser (Optional):**
```bash
python manage.py createsuperuser
```

2. **Collect Static Files:**
```bash
python manage.py collectstatic
```

3. **Configure Firewall:**
```bash
# Allow port 8000 through firewall
sudo ufw allow 8000
```

4. **Run with Gunicorn (Production):**
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn lottery_generator.wsgi:application --bind 0.0.0.0:8000
```

### Environment Variables (Optional)

Create a `.env` file for production settings:
```bash
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-domain.com,your-server-ip
```

## 🛠️ Troubleshooting

### Common Issues and Solutions

#### 1. **Port Already in Use**
```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill the process (replace PID with actual process ID)
sudo kill -9 PID

# Or use different port
python manage.py runserver 0.0.0.0:8080
```

#### 2. **Permission Denied**
```bash
# Fix permissions
chmod +x manage.py

# If database permission issues
sudo chown -R $USER:$USER .
```

#### 3. **Virtual Environment Issues**
```bash
# Deactivate and recreate virtual environment
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 4. **Migration Errors**
```bash
# Reset migrations if needed
rm -rf generator/migrations/000*.py
python manage.py makemigrations generator
python manage.py migrate
```

#### 5. **Module Not Found Errors**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

## 🧪 Testing Your Installation

Run this quick test to verify everything works:

```bash
# Test basic functionality
python manage.py check

# Test database connection
python manage.py showmigrations

# Test server startup (should show no errors)
python manage.py runserver --help
```

## 📊 Performance Tips

### For Better Performance on Linux Servers:

1. **Use SSD storage** for faster database access
2. **Allocate sufficient RAM** (minimum 2GB recommended)
3. **Use Gunicorn** for production deployment
4. **Enable caching** for better response times
5. **Use PostgreSQL** for production instead of SQLite

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly on Linux environment
5. Commit: `git commit -m "Add feature"`
6. Push: `git push origin feature-name`
7. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support & Contact

For questions, issues, or feature requests:

1. Create an issue on GitHub
2. **Check the troubleshooting section** above
3. **Review the usage guide** for common questions
4. **Contact the development team** for urgent issues

## 🏆 Acknowledgments

- **Django** framework for robust web development
- **Bootstrap** for responsive UI components
- **Texas Lottery** for official checking integration
- **Python community** for excellent libraries

---

**🎲 Ready to generate your winning numbers? Follow the installation guide above and start generating lottery combinations with advanced features!
updated to view last 10 combinations and also added the missing part of comparing results