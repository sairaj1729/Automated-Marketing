# LinkedIn AutoMarketer API

Backend API for the LinkedIn marketing automation tool built with FastAPI and MongoDB.

## Features

- User authentication (registration, login, logout)
- LinkedIn OAuth integration
- AI-powered content generation
- Post scheduling and automated publishing
- Analytics dashboard
- User settings management
- Email marketing capabilities

## Tech Stack

- **Framework**: FastAPI
- **Database**: MongoDB with Motor (async driver)
- **Authentication**: JWT tokens with OAuth2
- **AI Service**: OpenAI GPT
- **LinkedIn Integration**: LinkedIn Marketing API
- **Deployment**: Docker-ready

## Prerequisites

- Python 3.8+
- MongoDB
- LinkedIn Developer Account (for LinkedIn integration)
- OpenAI API Key (for AI features)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Copy `.env.example` to `.env` and fill in the values:
   ```bash
   cp .env.example .env
   ```

5. Start MongoDB (if not using Docker):
   ```bash
   mongod
   ```

## Running the Application

### Development Mode

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:3000`

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 3000
```

### Using Docker

```bash
docker-compose up --build
```

## API Documentation

Once the server is running, you can access:

- **Swagger UI**: `http://localhost:3000/docs`
- **ReDoc**: `http://localhost:3000/redoc`

## Project Structure

```
backend/
├── app/
│   ├── config/          # Configuration files
│   ├── models/          # MongoDB document models
│   ├── schemas/         # Pydantic schemas for validation
│   ├── api/             # API routes
│   │   └── v1/          # API version 1
│   │       └── routes/  # Individual route modules
│   ├── core/            # Business logic
│   └── utils/           # Utility functions
├── requirements.txt     # Python dependencies
├── .env                # Environment variables
├── Dockerfile          # Docker configuration
└── docker-compose.yml  # Multi-container setup
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `MONGODB_URL` | MongoDB connection string | Yes |
| `MONGODB_DATABASE` | MongoDB database name | Yes |
| `SECRET_KEY` | Secret key for JWT signing | Yes |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | Yes |
| `LINKEDIN_CLIENT_ID` | LinkedIn OAuth client ID | No |
| `LINKEDIN_CLIENT_SECRET` | LinkedIn OAuth client secret | No |
| `AI_API_KEY` | OpenAI API key | No |
| `AI_MODEL` | AI model to use | No |
| `EMAIL_HOST` | SMTP server hostname | No |
| `EMAIL_PORT` | SMTP server port | No |
| `EMAIL_USERNAME` | SMTP username | No |
| `EMAIL_PASSWORD` | SMTP password | No |
| `EMAIL_USE_TLS` | Use TLS for SMTP | No |
| `DEFAULT_FROM_EMAIL` | Default sender email | No |
| `FRONTEND_URL` | Frontend URL for CORS | Yes |

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login and get access token
- `POST /api/v1/auth/linkedin` - LinkedIn OAuth
- `POST /api/v1/auth/logout` - Logout

### Users
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me/settings` - Update user settings

### Posts
- `POST /api/v1/posts/generate` - Generate AI content
- `POST /api/v1/posts/scheduled` - Schedule a post
- `GET /api/v1/posts/scheduled` - Get all scheduled posts
- `GET /api/v1/posts/scheduled/{id}` - Get a specific scheduled post
- `PUT /api/v1/posts/scheduled/{id}` - Update a scheduled post
- `DELETE /api/v1/posts/scheduled/{id}` - Delete a scheduled post

### Analytics
- `GET /api/v1/analytics/` - Get analytics data
- `GET /api/v1/analytics/metrics` - Get key metrics
- `GET /api/v1/analytics/best-times` - Get optimal posting times

### Settings
- `GET /api/v1/settings/` - Get user settings
- `PUT /api/v1/settings/` - Update user settings

### Emails
- `POST /api/v1/emails/` - Send email
- `POST /api/v1/emails/with-attachment` - Send email with attachment

## Development

### Adding New Features

1. Create new models in `app/models/`
2. Create schemas in `app/schemas/`
3. Add routes in `app/api/v1/routes/`
4. Register routes in `app/api/v1/__init__.py`

### Running Tests

```bash
# TODO: Add test commands when tests are implemented
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

MIT License