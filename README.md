# 🎯 Russian Roulette Flask Game

A web-based simulation of Russian Roulette built with Flask, HTML, CSS, and JavaScript. This is a multiplayer game where players take turns "pulling the trigger" until someone gets the chamber with the bullet.

## ⚠️ Disclaimer

**This is a simulation game for entertainment purposes only.** It does not promote or encourage any real-world dangerous activities. Please play responsibly.

## 🎮 Features

- **Multiplayer Support**: 2-6 players can participate in a single game
- **Responsive Web Interface**: Works on desktop and mobile devices
- **Real-time Game State**: Dynamic updates as the game progresses
- **Interactive UI**: Smooth animations and visual feedback
- **Game Reset**: Easy reset functionality for multiple rounds
- **Player Management**: Add/remove players before starting
- **Session Management**: Maintains game state during play

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Clone or download the project:**
   ```bash
   cd russian-roulette
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```
   
   Or use the run script:
   ```bash
   python run.py
   ```

5. **Open your browser and navigate to:**
   ```
   http://localhost:5000
   ```

## 🎲 How to Play

1. **Start the Game**: Visit the homepage and click "Start New Game"
2. **Add Players**: Add 2-6 players to participate in the game
3. **Begin Playing**: Once you have enough players, start the game
4. **Take Turns**: Players take turns clicking "Pull Trigger"
5. **Win Condition**: The last player(s) standing after someone gets the bullet wins!

## 📁 Project Structure

```
russian-roulette/
├── app.py                 # Main Flask application
├── run.py                # Application runner script
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── README.md            # Project documentation
└── templates/           # HTML templates
    ├── base.html        # Base template with common styles
    ├── index.html       # Homepage
    ├── setup.html       # Player setup page
    └── game.html        # Main game interface
```

## 🛠️ Technical Details

### Backend (Python/Flask)

- **Flask Framework**: Lightweight web framework
- **Game Logic**: Pure Python implementation of Russian Roulette mechanics
- **Session Management**: Server-side game state management
- **REST API**: JSON endpoints for game actions

### Frontend (HTML/CSS/JavaScript)

- **Responsive Design**: Mobile-friendly interface
- **Interactive Elements**: Smooth animations and transitions
- **Real-time Updates**: AJAX calls for seamless gameplay
- **Modern Styling**: CSS3 with gradients and animations

### Key Components

#### Game Logic (`RussianRouletteGame` class)
- Manages chamber state and bullet position
- Handles player turns and game flow
- Determines win/loss conditions
- Provides game reset functionality

#### API Endpoints
- `POST /add_player` - Add a player to the game
- `POST /start_game` - Initialize a new game
- `POST /pull_trigger` - Execute a trigger pull
- `POST /reset_game` - Reset the current game
- `GET /get_game_state` - Get current game status

## 🔧 Configuration

The application can be configured through environment variables:

```bash
# Flask settings
export FLASK_ENV=development          # or 'production'
export FLASK_DEBUG=True              # Enable debug mode
export FLASK_HOST=0.0.0.0           # Host to bind to
export FLASK_PORT=5000              # Port to run on

# Security
export SECRET_KEY=your-secret-key-here  # Required for production
```

## 🎨 Customization

### Game Rules
You can modify the game rules in `app.py`:

```python
class RussianRouletteGame:
    def __init__(self):
        self.chamber_count = 6        # Number of chambers
        # ... other settings
```

### Styling
Customize the appearance by modifying the CSS in `templates/base.html`:

- Colors and gradients
- Animations and transitions
- Layout and spacing
- Responsive breakpoints

### Player Limits
Change player limits in `config.py`:

```python
MAX_PLAYERS = 6
MIN_PLAYERS = 2
```

## 🔒 Security Considerations

- **Secret Key**: Always use a strong secret key in production
- **HTTPS**: Enable HTTPS in production environments
- **Input Validation**: All user inputs are validated server-side
- **Session Security**: Secure session cookie settings for production

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Use a different port
   python app.py --port 8000
   ```

2. **Module not found errors:**
   ```bash
   # Make sure you're in the virtual environment
   pip install -r requirements.txt
   ```

3. **Template not found:**
   ```bash
   # Ensure you're running from the project root directory
   cd russian-roulette
   python app.py
   ```

## 🚀 Deployment

### Local Development
The application is configured for local development by default. Simply run:
```bash
python run.py
```

### Production Deployment
For production deployment:

1. Set environment variables:
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your-very-secure-secret-key
   ```

2. Use a production WSGI server like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📜 License

This project is open source and available under the MIT License.

## 🎯 Future Enhancements

- [ ] Sound effects and music
- [ ] Player statistics and scoring
- [ ] Multiple game modes
- [ ] Tournament bracket system
- [ ] Spectator mode
- [ ] Chat functionality
- [ ] Mobile app version
- [ ] Multiplayer lobbies

## 🆘 Support

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Review the code comments for implementation details
3. Create an issue in the project repository

---

**Remember: This is just a game! Play responsibly and have fun! 🎮**