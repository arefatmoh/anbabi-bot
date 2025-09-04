# Read & Revive (አንባቢ) - Telegram Reading Tracker Bot

A comprehensive, youth-led initiative to make reading more engaging, accessible, and rewarding for Muslim youth in Ethiopia through community-driven book discussions and gamified reading tracking.

## 🌟 **Project Status: Phase 1 - Foundation Complete** 🚀

**Current Version**: 2.0.0 (Professional Architecture)  
**Previous Version**: 1.0.0 (MVP)

## 🏗️ **New Professional Architecture**

### **Enhanced Features (v2.0)**
- 🆕 **Community Mode** - League-based reading with admin management
- 🎯 **Enhanced Gamification** - Advanced achievements and motivation system
- ⏰ **Smart Reminders** - Personalized reading notifications
- 📊 **Advanced Analytics** - Reading patterns and insights
- 🔧 **Admin Dashboard** - Comprehensive management tools
- 🎨 **Visual Elements** - Progress bars, badges, shareable certificates

### **Core Features (v1.0)**
- ✅ **User Registration** - Collect name, city, phone/email
- ✅ **Book Selection** - Choose from featured books or add custom
- ✅ **Progress Tracking** - Track pages read and calculate completion %
- ✅ **Motivation System** - Send encouraging feedback
- ✅ **Achievement System** - Unlock achievements for reading milestones
- ✅ **Data Export** - Admin can export to Excel/CSV

## 📁 **Professional File Structure**

```
anbabi-bot/
├── 📁 src/                          # Source code directory
│   ├── 📁 core/                     # Core bot functionality
│   │   ├── bot.py                   # Main bot orchestration
│   │   ├── 📁 handlers/             # Message and command handlers
│   │   ├── 📁 keyboards/            # Inline keyboard layouts
│   │   └── 📁 utils/                # Utility functions
│   ├── 📁 database/                 # Database layer
│   │   ├── database.py              # Database connection & setup
│   │   ├── 📁 models/               # Data models
│   │   └── 📁 repositories/         # Data access layer
│   ├── 📁 services/                 # Business logic layer
│   ├── 📁 features/                 # Feature modules
│   └── 📁 config/                   # Configuration
├── 📁 tests/                        # Test suite
├── 📁 admin/                        # Admin tools
├── 📁 assets/                       # Static assets
├── 📁 scripts/                      # Utility scripts
├── 📁 docs/                         # Documentation
├── main.py                          # Application entry point
├── requirements.txt                  # Python dependencies
└── README.md                        # This file
```

## 🚀 **Getting Started**

### **Prerequisites**
- Python 3.8 or higher
- Telegram Bot Token (get from [@BotFather](https://t.me/botfather))

### **Quick Start (5 minutes)**

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd anbabi-bot
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   ```bash
   # Copy the example file
   cp env_example.txt .env
   
   # Edit .env with your bot token
   BOT_TOKEN=your_actual_bot_token_here
   ADMIN_USER_IDS=your_telegram_user_id
   ```

3. **Initialize Database**
   ```bash
   python scripts/setup_database.py
   ```

4. **Start the Bot**
   ```bash
   python main.py
   ```

## 🔧 **Development & Testing**

### **Running Tests**
```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_database.py

# Run with coverage
python -m pytest --cov=src tests/
```

### **Code Quality**
```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/
```

### **Database Management**
```bash
# Initialize database
python scripts/setup_database.py

# Create backup
python scripts/backup.py

# Seed sample data
python scripts/seed_data.py
```

## 📊 **Database Schema (Enhanced)**

### **New Tables for Community Features**
- **leagues** - Community reading leagues
- **league_members** - League membership
- **reminders** - User notification preferences
- **achievements** - Enhanced achievement system

### **Enhanced Existing Tables**
- **users** - Added reading mode, daily goals, reminders
- **books** - Added categories, descriptions, cover images
- **user_books** - Added league support, target dates
- **reading_sessions** - Added reading time, notes

## 🎯 **Implementation Roadmap**

### **✅ Phase 1: Foundation (COMPLETED)**
- [x] Professional file structure
- [x] Enhanced database design
- [x] Configuration management
- [x] Basic bot framework

### **🔄 Phase 2: Community Features (IN PROGRESS)**
- [ ] League management system
- [ ] Community progress tracking
- [ ] Admin dashboard
- [ ] Member management

### **📋 Phase 3: Enhanced Gamification (PLANNED)**
- [ ] Advanced achievement system
- [ ] Motivation engine
- [ ] Visual elements
- [ ] Progress celebrations

### **📋 Phase 4: Smart Features (PLANNED)**
- [ ] Reminder system
- [ ] Analytics & insights
- [ ] Export tools
- [ ] Performance optimization

### **📋 Phase 5: Polish & Launch (PLANNED)**
- [ ] Testing & QA
- [ ] Documentation
- [ ] Deployment
- [ ] User feedback integration

## 🎮 **Bot Commands**

### **User Commands**
- `/start` - Start the bot and register
- `/help` - Show help information
- `/progress` - Update reading progress
- `/books` - Show current books
- `/stats` - Show reading statistics
- `/league` - League information and management
- `/reminder` - Set reading reminders
- `/profile` - View and edit profile

### **Admin Commands**
- `/setbook` - Set book for community league
- `/league` - Manage league settings
- `/members` - View league members
- `/export` - Export reading data
- `/report` - Generate system reports
- `/backup` - Create database backup
- `/cleanup` - Clean old data
- `/users` - View all users

## 🔒 **Security Features**

- User authentication through Telegram
- Admin-only access to sensitive operations
- Input validation and sanitization
- SQL injection protection through parameterized queries
- Rate limiting and abuse prevention

## 🚀 **Future Enhancements**

- Google Sheets integration for real-time data export
- Reading challenges and competitions
- Social features (reading groups, discussions)
- Advanced analytics and insights
- Multi-language support (Amharic, English)
- Reading recommendations based on user preferences
- Mobile app companion
- API for third-party integrations

## 🤝 **Contributing**

We welcome contributions! Please see our [Contributing Guidelines](docs/CONTRIBUTING.md).

### **Development Setup**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 **Support & Community**

- 📧 **Email**: [contact@readrevive.org](mailto:contact@readrevive.org)
- 💬 **Telegram**: [@ReadReviveBot](https://t.me/ReadReviveBot)
- 🐛 **Issues**: [GitHub Issues](https://github.com/readrevive/anbabi-bot/issues)
- 📖 **Documentation**: [docs/](docs/)

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **Telegram Bot API** for the platform
- **Python community** for excellent libraries
- **Muslim youth community in Ethiopia** for inspiration
- **All contributors and supporters** who believe in the power of reading

---

## 🎉 **Ready to Transform Reading Culture?**

**Read & Revive (አንባቢ)** is more than just a bot - it's a movement to inspire the next generation of readers in Ethiopia and beyond.

**Start your reading journey today!** 📚✨

---

*Last updated: September 2025*  
*Version: 2.0.0 - Professional Architecture*
