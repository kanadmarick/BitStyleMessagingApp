# BitStyle Messaging App

## Overview
Secure, real-time messaging with client-side AES encryption, Flask + SocketIO backend, and a responsive terminal-style UI. Optimized for desktop and mobile (iPhone Safari).

**Key Features:**
- 🔐 AES End-to-End Encryption
- 📱 Mobile-Optimized Interface  
- 💻 Terminal/Matrix-Style Design
- ⚡ Real-Time WebSocket Communication
- 👥 Two-User Room Limit
- 💾 Message Persistence with SQLite
- 🧪 Comprehensive Test Suite with Edge Cases
- 📊 Detailed Backend Logging
- 🚀 CI/CD (Jenkins Freestyle today; Jenkinsfile-ready)
- 🐳 Docker containerization
- ☸️ Kubernetes (Helm charts provided)
- 🏗️ Infrastructure as Code (Terraform)
- 🔧 Configuration Management (Ansible)

---

## Files (Top-Level)
- `app.py`: Flask + SocketIO backend server with auto-port selection and SQLite persistence
- `index.html`: Responsive frontend with terminal theme and touch optimization
- `messages.db`: SQLite database for message persistence
- `Dockerfile`: Multi-stage Docker build configuration
- `Makefile`: Handy dev/deploy shortcuts
- `DEPLOYMENT.md`: CI/CD setup (reference)
- **Infrastructure**:
  - `terraform/`: Infrastructure as Code for GCP free tier resources
  - `ansible/`: Configuration management and Kubernetes setup
  - `k8s/`: Kubernetes manifests for container orchestration
  - `.github/workflows/`: CI/CD pipeline configuration
- **Testing**:
  - `test_app.py`: Basic unit tests for server functionality
  - Other tests optional; see repo for additional suites
- `README.md`: This documentation file

---

## 🚀 CI/CD & Cloud Deployment

### Cloud Infrastructure (GCP Free Tier)
- **Compute Engine**: e2-micro VM instance (always free)
- **Container Registry**: Docker image storage
- **Kubernetes**: Kind cluster on VM for container orchestration
- **Networking**: Firewall rules and load balancing
- **Infrastructure as Code**: Terraform for reproducible deployments

### Automated Pipeline Stages
1. **GitHub Push**: Code pushed to main branch triggers webhook
2. **Jenkins Build**: Automated testing and Docker image creation  
3. **Terraform Deploy**: Infrastructure provisioning on GCP free tier
4. **Ansible Configure**: K3s cluster setup and system configuration
5. **Helm Deploy**: Application deployment with rolling updates
6. **Health Checks**: Automated verification and rollback on failure

### Jenkins (Freestyle today)
Access Jenkins at http://localhost:8080 and create a Freestyle job with shell steps:
- Run tests: `python3 -m pytest -q || true`
- Build image: `docker build -t bitstyle-messaging:$BUILD_NUMBER .`
- Run: `docker run -d --name messaging-app-$BUILD_NUMBER -p 500$BUILD_NUMBER:5000 bitstyle-messaging:$BUILD_NUMBER || true`
For full pipeline migration, you can switch to a Jenkinsfile once the Pipeline plugin is installed.

---

## Core Functionality

### 🔐 Secure User Authentication
- Users enter a unique username and shared encryption key
- Room key serves as both authentication and encryption password
- Maximum of two concurrent users per session
- Automatic user disconnect handling prevents "room full" errors

### 💻 Terminal-Style Interface
- Authentic monospace font for genuine terminal feel
- Black background with bright green (#00FF00) text
- Canvas-rendered ASCII art banner
- Minimalistic, distraction-free design
- Touch-optimized controls for mobile devices

### 🔒 Military-Grade Encryption
- AES-256 encryption using CryptoJS library
- Messages encrypted client-side before transmission
- Server never accesses plaintext content
- End-to-end encryption ensures complete privacy
- Encryption key never transmitted over network

### ⚡ Real-Time Communication
- WebSocket-based messaging via Flask-SocketIO
- Instant message delivery with typing indicators
- Automatic reconnection handling
- CORS enabled for cross-origin access
- Auto-port selection to avoid conflicts

### 📱 Mobile Optimization
- Responsive design optimized for iPhone Safari
- Touch-friendly interface with 44px minimum touch targets
- Viewport meta tags for proper mobile scaling
- Touch-action properties for smooth interaction
- Tested and verified on iOS Safari browser

### 👥 Smart Room Management
- Enforced two-user limit per room with immediate disconnect
- Message persistence across sessions using SQLite database
- Message history automatically loaded on user join
- Graceful handling of user disconnections
- Prevents duplicate connections from same user
- User color assignment for message identification
- Automatic cleanup of disconnected sessions
- Detailed backend logging for debugging and monitoring

---

## Technical Architecture

### Backend (`app.py`)
- **Framework**: Flask with Flask-SocketIO for WebSocket support
- **Database**: SQLite for message persistence with automatic table creation
- **Auto-Port Selection**: Automatically finds an open port (tries 5001-5010). Also honors `PORT` env var.
- **CORS Configuration**: Enabled for cross-origin requests (`cors_allowed_origins='*'`)
- **Event Handling**:
  - `join`: User authentication, room assignment, and history delivery
  - `message`: Encrypted message relay and database storage
  - `disconnect`: Cleanup and user removal from rooms
- **API Endpoints**:
  - `/history`: REST endpoint for retrieving message history
- **Room Management**: Strict two-user limit with immediate disconnect for third user
- **User Tracking**: Maintains active user lists and prevents duplicates
- **Logging**: Comprehensive backend logging for joins, disconnects, and errors

### Frontend (`index.html`)
- **Responsive Design**: Mobile-first approach with viewport optimization
- **Canvas Graphics**: ASCII art banner with dynamic terminal effects
- **CryptoJS Integration**: Client-side AES encryption/decryption
- **Touch Optimization**: 44px minimum touch targets for mobile devices
- **Theme System**: Terminal aesthetic with monospace fonts and green-on-black color scheme
- **SocketIO Client**: Real-time communication with automatic reconnection
- **Error Handling**: User-friendly error messages and connection status

### Testing Suite
- **Unit Tests** (`test_app_detailed.py`): Comprehensive backend functionality testing
- **Integration Tests** (`test_integration.py`): End-to-end messaging scenarios with edge cases
- **Negative Tests**: Invalid usernames, duplicate users, invalid message types, send after disconnect
- **Edge Cases**: Room full scenarios, missing fields, empty/long messages, rapid join/leave
- **Persistence Tests**: Message storage and retrieval across sessions
- **Test Coverage**: User authentication, room limits, message encryption, disconnect handling
- **Verbose Output**: Detailed logging and assertions for debugging
- **Automated Testing**: Run via unittest framework with comprehensive assertions

---

## Security Architecture

### 🔐 Encryption Implementation
- **Algorithm**: AES-256 with CryptoJS library
- **Client-Side Only**: All encryption/decryption happens in browser
- **Zero-Knowledge**: Server never accesses plaintext messages
- **Key Management**: Room key serves as encryption password
- **Message Persistence**: Encrypted messages stored in SQLite database
- **History Delivery**: Previous encrypted messages loaded on join

### 🛡️ Security Measures
- **Input Validation**: Sanitized user inputs prevent XSS attacks
- **CORS Policy**: Controlled cross-origin resource sharing
- **Session Management**: Secure WebSocket connections with session tracking
- **Error Handling**: No sensitive information leaked in error messages
- **Network Security**: All encryption keys remain client-side

### ⚠️ Security Considerations
- **Key Sharing**: Room key must be shared through secure channels
- **Browser Security**: Depends on client-side browser security
- **Local Storage**: Encryption keys stored temporarily in browser memory
- **Network Traffic**: Only encrypted messages transmitted over network

---

## Installation & Setup

### Prerequisites
- Python 3.12 or higher
- pip package manager
- Modern web browser (Safari, Chrome, Firefox)
- Internet connection for CDN resources

### Quick Start
```bash
# 1. Clone the repository
git clone https://github.com/kanadmarick/BitStyleMessagingApp.git
cd BitStyleMessagingApp

# 2. Create virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install flask flask-socketio python-socketio requests pytest

# 4. Start the server
python app.py
# The app will print the chosen URLs, e.g. http://127.0.0.1:5001
```

### Server will automatically:
- Find an available port (5001-5010)
- Enable CORS for cross-origin requests
- Display server URLs for local and network access
- Handle graceful shutdown with Ctrl+C

### Access Options
- **Local**: http://127.0.0.1:PORT
- **Network**: http://YOUR_LOCAL_IP:PORT (shown in terminal)
- **Mobile**: Use network IP for iPhone Safari access

---

## Testing

### Run Tests
```bash
pytest -q || python -m unittest -v
```

### Test Coverage
- ✅ User authentication and validation
- ✅ Two-user room limit enforcement with immediate disconnect
- ✅ Message encryption/decryption
- ✅ Message persistence and history retrieval
- ✅ Real-time message delivery
- ✅ User disconnect handling
- ✅ Error handling and edge cases
- ✅ Integration with SocketIO clients
- ✅ Negative test cases (invalid inputs, duplicate users)
- ✅ Edge cases (room full, missing fields, empty/long messages)

---

## Mobile Usage (iPhone Safari)

### Accessing on iPhone
1. **Find Network IP**: Check server startup logs for network URL
2. **Open Safari**: Navigate to http://YOUR_NETWORK_IP:PORT
3. **Add to Home Screen**: Tap share button → "Add to Home Screen" for app-like experience
4. **Full Screen**: Website optimized for mobile viewport and touch interaction

### Touch-Optimized Features
- **Large Touch Targets**: 44px minimum size for all interactive elements
- **Smooth Scrolling**: Optimized message area scrolling
- **Keyboard Handling**: Proper input focus and virtual keyboard support
- **Responsive Layout**: Adapts to different screen orientations

### Sharing Options
- **Local Network**: Share network IP with others on same WiFi
- **External Access**: Use ngrok or similar tunneling service
- **Cloud Deployment**: Deploy to Heroku, AWS, or similar platforms

---

## Development & Customization

### Code Structure
```
BitStyleMessagingApp/
├── app.py                 # Flask server with SocketIO and SQLite
├── index.html            # Frontend with terminal theme
├── messages.db           # SQLite database for message persistence
├── test_app.py           # Basic unit tests
├── test_app_detailed.py  # Comprehensive tests
├── test_integration.py   # Integration and edge case testing
├── README.md             # Documentation
└── __pycache__/          # Python cache files
```

### Customization Options
- **Theme Colors**: Modify CSS variables for different color schemes
- **Fonts**: Change monospace font family in CSS
- **Room Capacity**: Update user limit in `app.py`
- **Port Range**: Modify auto-port selection range
- **Canvas Graphics**: Update ASCII art in canvas rendering

### Adding Features
- **Enhanced Logging**: Backend includes detailed join/disconnect/error logging
- **Message History**: Database integration with SQLite for persistence ✅
- **File Sharing**: Implement encrypted file transfer
- **Voice Messages**: Add WebRTC audio recording
- **Typing Indicators**: Real-time typing status
- **User Avatars**: Profile picture integration
- **Message Search**: Search through persistent message history

---

## Troubleshooting

### Common Issues

#### "Room is full" Error
- **Cause**: Two users already connected or previous session not cleaned up
- **Solution**: Third user is immediately disconnected with detailed backend logging
- **Debug**: Check server logs for explicit disconnect messages

#### Connection Issues
- **Cause**: Port conflicts or firewall blocking
- **Solution**: Server auto-selects available ports, check firewall settings

#### Mobile Display Issues
- **Cause**: Viewport not configured properly
- **Solution**: Ensure viewport meta tag present, test in private browsing

#### Encryption Errors
- **Cause**: Mismatched room keys between users
- **Solution**: Ensure both users enter identical room key

#### Performance Issues
- **Cause**: Multiple server instances or resource conflicts
- **Solution**: Check for running processes, restart with single instance

### Debug Mode
```bash
# Run with debug information
export FLASK_ENV=development
python app.py
```

---

## Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`python -m unittest discover`)
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open Pull Request

### Code Standards
- **Python**: Follow PEP 8 style guidelines
- **JavaScript**: Use ES6+ modern syntax
- **CSS**: Mobile-first responsive design
- **Testing**: Maintain >90% test coverage

---

## License & Contact

### Repository
- **GitHub**: [kanadmarick/BitStyleMessagingApp](https://github.com/kanadmarick/BitStyleMessagingApp)
- **Issues**: Report bugs and feature requests via GitHub Issues
- **Contributions**: Pull requests welcome!

### Technical Support
- Check existing GitHub Issues before creating new ones
- Include error messages and browser/OS information
- Test with minimal configuration before reporting

---

## Changelog

### v3.0.0 (Latest)
- ✅ Message persistence with SQLite database
- ✅ Message history loaded on user join
- ✅ REST API endpoint for message history
- ✅ Comprehensive edge case testing
- ✅ Negative test cases for invalid inputs
- ✅ Detailed backend logging for debugging
- ✅ Strict room limit enforcement with immediate disconnect
- ✅ Enhanced integration test suite

### v2.0.0
- ✅ Terminal theme with monospace fonts
- ✅ iPhone Safari optimization
- ✅ Touch-friendly interface
- ✅ Integration test suite
- ✅ Auto-port selection
- ✅ User disconnect handling
- ✅ CORS configuration
- ✅ Comprehensive documentation

### v1.0.0 (Initial)
- ✅ Basic messaging functionality
- ✅ End-to-end encryption
- ✅ Two-user room limit
- ✅ WebSocket real-time communication
- ✅ Unit test coverage
