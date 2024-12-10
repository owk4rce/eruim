# Eruim: Cultural Events API

A RESTful API for managing cultural events and venues in Israel, supporting multiple languages (English, Russian, Hebrew).

## Features

### Core Functionality
- Event Management (CRUD operations)
- Venue Management
- Multi-language Support (EN, RU, HE)
- User Authentication and Authorization
- Image Upload and Management
- Geocoding Integration
- Automated Translation
- Real-time Updates

### Security Features
- JWT-based Authentication
- Role-based Access Control
- Rate Limiting
- CORS Protection
- HTTP-only Cookies
- Input Validation
- Error Handling

### Technical Features
- Automated Event Status Updates
- Account Cleanup System
- Logging System
- Swagger Documentation
- Custom Decorators

## Technology Stack

- **Backend Framework**: Flask
- **Database**: MongoDB with Mongoengine ODM
- **Authentication**: JWT (Flask-JWT-Extended)
- **Documentation**: Swagger/OpenAPI (Flasgger)
- **External Services**:
  - HERE Maps API (Geocoding)
  - GeoNames API (City Validation)
  - Google Translate API (Auto-translation)

## Project Structure

```
backend/
├── src/
│   ├── config/           # Configuration modules
│   ├── controllers/      # Business logic
│   ├── models/          # Database models
│   ├── routes/          # API endpoints
│   └── utils/           # Helper functions
├── logs/                # Application logs
└── uploads/             # User uploaded files
```

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd [project-directory]
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables in `.env`:
```env
DB_PATH=mongodb://localhost:27017
DB_NAME=eruim
GEONAMES_USERNAME=your_username
HERE_API_KEY=your_api_key
JWT_SECRET_KEY=your_secret_key
APP_SERVICE_EMAIL=your_email
APP_SERVICE_EMAIL_PASSWORD=your_password
DEBUG=true
MAX_FILE_SIZE=5242880
```

5. Run the application:
```bash
python run.py
```

## API Documentation

The API documentation is available at `/api/v1/docs` when the server is running. It provides detailed information about:
- Available endpoints
- Request/Response formats
- Authentication requirements
- Example requests

### Main Endpoints

- **Authentication**: `/api/v1/auth/*`
  - Register, Login, Logout
  - Password Reset
  - Email Confirmation

- **Events**: `/api/v1/events`
  - Create, Read, Update, Delete events
  - Filter by city, venue, status
  - Image upload support

- **Venues**: `/api/v1/venues`
  - Manage venue information
  - Geocoding integration
  - Multi-language support

- **Users**: `/api/v1/users`
  - User management (admin only)
  - Role-based access control

## Security

### Authentication
- JWT tokens for authentication
- HTTP-only cookies for token storage
- Token expiration and refresh mechanism

### Authorization Levels
1. **Admin**: Full system access
2. **Manager**: Content management access
3. **User**: Basic access with favorites functionality

### Rate Limiting
- Public routes: 30 requests per minute
- Auth routes: 3 requests per minute, 9 per hour
- Protected routes:
  - Admin: 60 requests per minute
  - Manager: 40 requests per minute
  - User: 20 requests per minute

## Automated Tasks

The application includes several automated maintenance tasks:

1. **Event Status Updates**
   - Automatically deactivates past events
   - Runs daily at midnight

2. **Account Cleanup**
   - Removes unactivated accounts after 48 hours
   - Maintains database cleanliness

## Error Handling

The application implements comprehensive error handling:

- Custom error classes for different scenarios
- Standardized error responses
- Detailed logging system
- Input validation at multiple levels

## Logging

Logs are stored in the `logs/` directory with the following features:
- Daily rotation
- Size-based rotation (10MB limit)
- Different log levels based on environment
- Comprehensive error tracking

## Development

### Code Style
- PEP 8 compliance
- Comprehensive docstrings
- English comments

## Future Development Plans

### Frontend Development
- Modern web interface
- Responsive design for mobile devices
- Interactive maps for venue locations
- Advanced search and filtering capabilities
- Multi-language interface

### Enhanced User Engagement
- Email notification system for favorite events
  - Reminders 48 hours before event start
  - Updates about significant changes (cancellations, time changes)
- Social sharing features
- User preferences settings

### AI Integration
- Automated event collection from various sources
  - Web scraping of cultural websites
  - Natural Language Processing for content extraction
  - Automatic categorization of events
  - Duplicate detection and merging
- Automated content translation improvements

### System Improvements
- Caching system for better performance
- Extended API functionality
