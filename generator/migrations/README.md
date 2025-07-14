# Enhanced Lottery Number Generator

A comprehensive Django web application for generating, managing, and checking lottery combinations with advanced features for both Mega Millions and Powerball games.

## 🎯 New Features

### 1. Seeded Number Generation
- Generate lottery combinations starting with a specific number
- Ensures your favorite number is always included
- Perfect for players who have lucky numbers

### 2. Combination Management
- Save and name your lottery combinations
- Check saved combinations against historical draws
- Compare combinations with Texas Lottery results
- Bulk check all saved combinations at once

### 3. Texas Lottery Integration
- Direct links to Texas Lottery check pages
- Fetch latest results (simulation for demo)
- Compare your numbers with recent draws
- Real-time checking capabilities

### 4. Export Functionality
- Export generated combinations to CSV or Excel
- Filter exports by date range and game type
- Track export history and statistics
- Perfect for record keeping

### 5. Dual Game Support
- Support for both Mega Millions and Powerball
- Separate data management for each game
- Game-specific number ranges and rules
- Unified interface for both games

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd lottery_project
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

5. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## 📊 Usage Guide

### Importing Lottery Data

#### Via Web Interface
1. Navigate to the "Import Data" tab
2. Select game type (Mega Millions or Powerball)
3. Upload Excel file with historical draw data
4. Click "Import Data"

#### Via Command Line
```bash
# Import Mega Millions data
python manage.py import_lottery_data data/mega_millions_2024.xlsx --game-type mega_millions

# Import Powerball data
python manage.py import_lottery_data data/powerball_2024.xlsx --game-type powerball
```

### Generating Numbers

#### Random Generation
1. Select game type
2. Choose number of combinations (1-100)
3. Click "Generate Random Numbers"

#### Seeded Generation
1. Select game type
2. Enter your favorite first number
3. Choose number of combinations
4. Click "Generate Seeded Numbers"

### Managing Saved Combinations

#### Saving Combinations
1. Go to "Save Numbers" tab
2. Enter combination name
3. Select game type
4. Enter your 5 main numbers (comma-separated)
5. Enter mega/power ball number
6. Click "Save Combination"

#### Checking Combinations
1. Go to "Saved Numbers"
2. Click "Check History" for historical comparison
3. Click "Check Texas" for Texas Lottery comparison
4. View detailed match results and prize information

### Exporting Data

#### Export Options
- **CSV Format**: Simple text format for spreadsheet applications
- **Excel Format**: Rich formatting with multiple columns
- **Date Filtering**: Export only combinations from specific date ranges

#### Export Process
1. Navigate to results page
2. Click "Export CSV" or "Export Excel"
3. File will download automatically
4. Export logged in system for tracking

## 🎮 Game Rules

### Mega Millions
- **Main Numbers**: 5 numbers from 1-70
- **Mega Ball**: 1 number from 1-25
- **Drawings**: Twice weekly (Tuesday & Friday)

### Powerball
- **Main Numbers**: 5 numbers from 1-69
- **Power Ball**: 1 number from 1-26
- **Drawings**: Three times weekly (Monday, Wednesday & Saturday)

## 🏆 Prize Tiers

### Mega Millions Prize Structure
- **Jackpot**: 5 + Mega Ball
- **Match 5**: $1,000,000
- **Match 4 + MB**: $10,000
- **Match 4**: $500
- **Match 3 + MB**: $200
- **Match 3**: $10
- **Match 2 + MB**: $10
- **Match 1 + MB**: $4
- **Match MB**: $2

### Powerball Prize Structure
- **Jackpot**: 5 + Power Ball
- **Match 5**: $1,000,000
- **Match 4 + PB**: $50,000
- **Match 4**: $100
- **Match 3 + PB**: $100
- **Match 3**: $7
- **Match 2 + PB**: $7
- **Match 1 + PB**: $4
- **Match PB**: $4

## 🔧 API Endpoints

### Generate Numbers
```http
GET /api/generate/?game_type=mega_millions&count=10&seed_number=7
```

### Check Numbers
```http
POST /api/check/
Content-Type: application/json

{
    "main_numbers": [1, 15, 22, 35, 67],
    "mega_ball": 7,
    "game_type": "mega_millions"
}
```

## 📁 File Structure

```
lottery_project/
├── lottery_generator/
│   ├── models.py              # Enhanced data models
│   ├── views.py               # Enhanced view functions
│   ├── utils.py               # Utility functions
│   ├── urls.py                # URL routing
│   ├── admin.py               # Admin interface
│   ├── templates/
│   │   └── lottery_generator/
│   │       ├── index.html           # Main homepage
│   │       ├── saved_combinations.html  # Saved numbers management
│   │       ├── check_results.html   # Check results display
│   │       └── results.html         # Generated numbers display
│   ├── management/
│   │   └── commands/
│   │       └── import_lottery_data.py
│   └── migrations/
├── requirements.txt
└── README.md
```

## 🔒 Security Features

- CSRF protection on all forms
- Input validation for number ranges
- SQL injection prevention
- XSS protection
- Secure file upload handling

## 🌟 Advanced Features

### Bulk Operations
- Bulk check all saved combinations
- Batch export functionality
- Mass import capabilities

### Analytics
- Match rate statistics
- Prize tier analysis
- Historical performance tracking
- Export usage logs

### Mobile API
- RESTful API for mobile apps
- JSON responses
- Error handling
- Rate limiting ready

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support or questions:
1. Check the documentation
2. Search existing issues
3. Create a new issue with details
4. Contact the development team

## 🎲 Disclaimer

This application is for entertainment purposes only. Please gamble responsibly and within your means. The lottery is a game of chance, and past results do not guarantee future outcomes.

---

**Happy number generating! 🍀**