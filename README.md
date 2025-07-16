# 🎲 Enhanced Lottery Number Generator

**Advanced lottery number generator with bulk seeded generation, Texas Lottery integration, and modern responsive UI.**

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/django-5.2-green.svg)](https://djangoproject.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## ✨ Enhanced Features

### 🎯 **Bulk Generation with Multiple First Numbers**
- Generate lottery combinations using multiple seed numbers at once
- Example: Enter `1, 3, 5` to create Powerball sets starting with each number
- Perfect for systematic lottery play strategies
- Visual grouping by seed number for easy organization

### 🌱 **Advanced Seeded Generation**
- **Single Seed**: Generate combinations starting with one lucky number
- **Bulk Seeds**: Generate combinations starting with multiple numbers
- **Seed Tracking**: See which seed number was used for each combination
- **Smart Validation**: Automatic range checking for different game types

### 💾 **Save & Manage Combinations**
- Save your favorite lottery combinations with custom names
- Check saved combinations against historical draws
- Bulk operations for managing multiple combinations
- Prize tier calculation and win tracking

### 📊 **Enhanced Export Features**
- Export combinations to CSV with detailed metadata
- Filter exports by date range and generation method
- Track which seed numbers were used
- Professional formatting with timestamps

### 🏴󠁵󠁳󠁴󠁸󠁿 **Texas Lottery Integration**
- Direct links to official Texas Lottery checking pages
- Quick access to Mega Millions and Powerball tools
- Latest results fetching capabilities
- Seamless integration with official lottery website

### 🎨 **Modern Responsive UI**
- Bootstrap 5 with clean, professional design
- Tabbed navigation for organized workflow
- Mobile-responsive for all devices
- Interactive bulk selection and management tools
- Animated number displays with game-specific styling

---

## 🖥️ **Linux Server Installation Guide**

### **Prerequisites**
- Ubuntu 18.04+ / CentOS 7+ / Any modern Linux distribution
- Python 3.8 or higher
- Git
- Internet connection

### **Step 1: System Dependencies**

#### **For Ubuntu/Debian:**
```bash
# Update package list
sudo apt update

# Install Python, pip, and git
sudo apt install python3 python3-pip python3-venv git -y

# Verify installations
python3 --version
pip3 --version
git --version
For CentOS/RHEL:
bash# Install Python, pip, and git
sudo yum install python3 python3-pip git -y

# Or for newer versions:
sudo dnf install python3 python3-pip git -y

# Verify installations
python3 --version
pip3 --version
git --version
Step 2: Clone Repository
bash# Remove any existing version
rm -rf lottery-number-generator

# Clone the enhanced repository
git clone https://github.com/tanzeelgcuf/lottery-number-generator.git

# Navigate to project directory
cd lottery-number-generator

# Verify project structure
ls -la
EPF
