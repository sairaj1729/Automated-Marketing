# LinkedIn AutoMarketer

A comprehensive LinkedIn marketing automation platform that combines AI-powered content generation, intelligent scheduling, and analytics to help professionals and businesses optimize their LinkedIn presence.

## 🚀 Features

### AI-Powered Content Generation
- Generate engaging LinkedIn posts using multiple AI providers
- Customizable tone (professional, casual, inspirational, educational)
- Audience targeting capabilities
- Reference URL integration for content inspiration
- Real-time content preview

### Smart Scheduling
- Schedule posts for optimal engagement times
- Timezone-aware scheduling across global timezones
- Calendar view for visual post management
- Automatic publishing at scheduled times
- Post status tracking (pending/published/failed)

### LinkedIn Integration
- Secure OAuth2 authentication
- Automatic token refresh management
- Direct posting to LinkedIn
- Engagement metrics collection
- Profile synchronization

### Analytics Dashboard
- Performance metrics tracking
- Engagement rate analysis
- Best posting time recommendations
- Heatmap visualization of optimal times
- Historical performance data

### Additional Features
- Email sharing with attachments
- Responsive glassmorphism UI design
- User authentication and profile management
- Cross-platform compatibility
- Real-time notifications

## 🏗️ Architecture

### Backend (FastAPI + Python)
```
backend/
├── app/
│   ├── api/v1/
│   │   ├── routes/
│   │   │   ├── auth.py          # User authentication
│   │   │   ├── posts.py         # Post management
│   │   │   ├── linkedin_auth.py # LinkedIn OAuth
│   │   │   ├── analytics.py     # Analytics endpoints
│   │   │   ├── emails.py        # Email functionality
│   │   │   └── settings.py      # User settings
│   │   └── deps.py              # Dependency injection
│   ├── core/
│   │   ├── ai_service.py        # AI content generation
│   │   ├── linkedin_service.py  # LinkedIn API integration
│   │   ├── scheduler.py         # Background task scheduler
│   │   ├── security.py          # Authentication utilities
│   │   └── email_service.py     # Email service
│   ├── models/
│   │   ├── user.py              # User data model
│   │   ├── scheduled_post.py    # Scheduled post model
│   │   ├── generated_post.py    # Generated post model
│   │   └── analytics.py         # Analytics data model
│   ├── schemas/
│   │   ├── auth.py              # Authentication schemas
│   │   ├── post.py              # Post schemas
│   │   ├── user.py              # User schemas
│   │   └── analytics.py         # Analytics schemas
│   ├── config/
│   │   ├── database.py          # Database configuration
│   │   └── settings.py          # Application settings
│   └── utils/
│       ├── helpers.py           # Utility functions
│       └── exceptions.py        # Custom exceptions
└── main.py                      # Application entry point
```

### Frontend (React + TypeScript)
```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/                  # Reusable UI components
│   │   ├── Layout.tsx           # Main application layout
│   │   ├── LinkedInPreviewModal.tsx
│   │   ├── EmailPreviewModal.tsx
│   │   └── SchedulePostModal.tsx
│   ├── context/
│   │   └── AuthContext.tsx      # Authentication context
│   ├── hooks/
│   │   └── useAuth.ts           # Authentication hook
│   ├── pages/
│   │   ├── Dashboard.tsx        # Main dashboard
│   │   ├── Generate.tsx         # Content generator
│   │   ├── Schedule.tsx         # Post scheduler
│   │   ├── Analytics.tsx        # Analytics dashboard
│   │   ├── SettingsPage.tsx     # User settings
│   │   ├── Login.tsx            # Login page
│   │   ├── Register.tsx         # Registration page
│   │   └── LinkedInCallback.tsx # OAuth callback handler
│   ├── services/
│   │   └── linkedinService.ts   # LinkedIn API service
│   ├── App.tsx                  # Main application component
│   └── main.tsx                 # Application entry point
├── public/
└── package.json
```

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.104.1
- **Database**: MongoDB with Motor async driver
- **Authentication**: JWT with OAuth2
- **AI Providers**: OpenRouter, Together AI, Hugging Face
- **Task Scheduling**: AsyncIO-based custom scheduler
- **Environment**: Python 3.8+

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS + shadcn/ui
- **State Management**: React Context API
- **Routing**: React Router v6
- **Animations**: Framer Motion
- **Data Fetching**: React Query

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB instance
- LinkedIn Developer Account
- AI Provider API Keys (optional)

### Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Create environment file:**
```bash
cp .env.example .env
```

5. **Configure environment variables in `.env`:**
```env
# Database Configuration
MONGODB_URL=mongodb://localhost:27017/linkedin_marketing
MONGODB_DATABASE=linkedin_marketing

# Security
SECRET_KEY=your-super-secret-jwt-key-here

# LinkedIn API Configuration
LINKEDIN_CLIENT_ID=your_linkedin_app_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_app_client_secret
LINKEDIN_REDIRECT_URI=http://localhost:8080/callback

# AI Service Configuration (optional)
OPENROUTER_API_KEY=your_openrouter_api_key
TOGETHER_API_KEY=your_together_api_key
HUGGING_FACE_API_KEY=your_huggingface_api_key

# Frontend URL for CORS
FRONTEND_URL=http://localhost:8080
```

6. **Start the backend server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 3000
```

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Create environment file:**
```bash
cp .env.example .env
```

4. **Configure environment variables in `.env`:**
```env
# Backend API Configuration
VITE_API_BASE_URL=http://localhost:3000
VITE_BACKEND_URL=http://localhost:3000

# LinkedIn OAuth Configuration
VITE_LINKEDIN_REDIRECT_URI=http://localhost:8080/callback
```

5. **Start the development server:**
```bash
npm run dev
```

### LinkedIn App Configuration

1. **Create LinkedIn App:**
   - Go to [LinkedIn Developer Portal](https://www.linkedin.com/developers/)
   - Create a new app
   - Add redirect URLs: `http://localhost:8080/callback`
   - Enable necessary permissions: `openid`, `profile`, `email`, `w_member_social`

2. **Configure OAuth Scopes:**
   - `openid`: User identification
   - `profile`: Basic profile information
   - `email`: Email address access
   - `w_member_social`: Post creation permissions

## 📊 Database Schema

### Users Collection
```javascript
{
  _id: ObjectId,
  email: String,
  hashed_password: String,
  linkedin_token: String,
  linkedin_refresh_token: String,
  linkedin_profile: {
    name: String,
    headline: String,
    picture: String
  },
  settings: {
    notifications: {
      postReminders: Boolean,
      engagementAlerts: Boolean,
      weeklyReports: Boolean
    },
    theme: String,
    timezone: String
  },
  created_at: DateTime,
  updated_at: DateTime
}
```

### Scheduled Posts Collection
```javascript
{
  _id: ObjectId,
  user_id: String,
  content: String,
  scheduled_datetime: DateTime (UTC),
  timezone: String,
  status: String, // pending, published, failed
  linkedin_post_id: String,
  error_message: String,
  created_at: DateTime,
  updated_at: DateTime
}
```

### Generated Posts Collection
```javascript
{
  _id: ObjectId,
  user_id: String,
  topic: String,
  tone: String,
  audience: String,
  url: String,
  generated_content: String,
  created_at: DateTime
}
```

## 🔐 Authentication Flow

### User Authentication
1. User registers/logs in through frontend
2. Backend validates credentials and generates JWT token
3. Token stored in localStorage
4. Token included in Authorization header for protected requests
5. Backend validates token using dependency injection

### LinkedIn OAuth Flow
1. User clicks "Connect LinkedIn" in settings
2. Frontend redirects to backend OAuth endpoint
3. Backend redirects to LinkedIn authorization page
4. User authenticates with LinkedIn
5. LinkedIn redirects back with authorization code
6. Backend exchanges code for access token
7. Tokens stored in user document and localStorage

## 🤖 AI Content Generation

### Supported Providers
1. **OpenRouter** (Primary) - Mistral-7B free model
2. **Together AI** (Secondary) - Mixtral-8x7B model
3. **Hugging Face** (Tertiary) - Various open models
4. **Local Llama** (Fallback) - Optional local inference

### Content Generation Process
1. User provides topic, tone, and audience
2. System tries providers in order of preference
3. AI generates content with proper LinkedIn formatting
4. Content cleaned and formatted for platform
5. Fallback to sample posts if all providers fail

### Prompt Engineering
- Customizable tone descriptions
- Audience targeting
- Content structure guidelines
- Hashtag recommendations
- Engagement optimization

## ⏰ Scheduling System

### Scheduler Architecture
- Async background task running every 60 seconds
- UTC-based time storage for consistency
- Automatic timezone conversion for display
- Token refresh handling before posting
- Error handling and retry logic

### Scheduling Workflow
1. User schedules post with local time and timezone
2. Time converted to UTC for storage
3. Scheduler checks for due posts every minute
4. Posts published to LinkedIn when time arrives
5. Status updated in database
6. User notified of success/failure

## 📈 Analytics System

### Data Collection
- LinkedIn engagement metrics (likes, comments, shares)
- Post reach and impressions
- Best posting time analysis
- User performance tracking

### Metrics Calculation
- Engagement rate: (likes + comments + shares) / reach
- Performance trends over time
- Optimal posting time identification
- Comparative analysis

### Visualization
- Interactive dashboard with key metrics
- Heatmap for best posting times
- Performance trend charts
- Comparative data displays

## 🐳 Deployment

### Docker Setup

**Backend Dockerfile:**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000"]
```

**Frontend Dockerfile:**
```dockerfile
FROM node:16-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
```

### Docker Compose
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "3000:3000"
    environment:
      - MONGODB_URL=mongodb://mongo:27017/linkedin_marketing
    depends_on:
      - mongo

  frontend:
    build: ./frontend
    ports:
      - "8080:80"
    depends_on:
      - backend

  mongo:
    image: mongo:latest
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db

volumes:
  mongodb_data:
```

## 🧪 Testing

### Backend Testing
```bash
# Run tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html
```

### Frontend Testing
```bash
# Run tests
npm test

# Run tests with coverage
npm test -- --coverage
```

## 📝 API Documentation

API documentation is automatically generated by FastAPI and available at:
- **Swagger UI**: `http://localhost:3000/docs`
- **ReDoc**: `http://localhost:3000/redoc`

### Key Endpoints

**Authentication:**
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login

**Posts:**
- `POST /api/v1/posts/generate` - Generate AI content
- `POST /api/v1/posts/scheduled` - Schedule post
- `GET /api/v1/posts/scheduled` - Get scheduled posts
- `POST /api/v1/posts/linkedin` - Post to LinkedIn

**LinkedIn:**
- `GET /api/v1/linkedin/auth` - Initiate OAuth
- `POST /api/v1/linkedin/callback` - Handle OAuth callback

**Analytics:**
- `GET /api/v1/analytics/` - Get analytics data
- `GET /api/v1/analytics/metrics` - Get metrics
- `GET /api/v1/analytics/best-times` - Get best posting times

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Follow existing code style and conventions
- Write comprehensive tests for new features
- Update documentation when making changes
- Ensure all tests pass before submitting PR
- Use descriptive commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Common Issues

**LinkedIn OAuth Not Working:**
- Verify LinkedIn app configuration
- Check redirect URLs match exactly
- Ensure all required scopes are enabled
- Confirm environment variables are set correctly

**AI Generation Failing:**
- Verify API keys are valid and active
- Check network connectivity to AI providers
- Review logs for specific error messages
- Test fallback to sample posts

**Scheduling Issues:**
- Verify MongoDB connection
- Check timezone settings
- Review scheduler logs
- Ensure backend is running continuously

### Getting Help
- Check existing issues on GitHub
- Review API documentation
- Examine application logs
- Contact maintainers for support

## 🚀 Future Roadmap

### Planned Features
- [ ] Real-time analytics with WebSocket
- [ ] A/B testing for post performance
- [ ] Team collaboration features
- [ ] Advanced scheduling algorithms
- [ ] Multi-platform social media integration
- [ ] Comprehensive test suite
- [ ] Performance monitoring and caching
- [ ] Mobile application
- [ ] Advanced analytics and reporting
- [ ] Content calendar view

### Technical Improvements
- [ ] Database indexing optimization
- [ ] Caching layer implementation
- [ ] Rate limiting and throttling
- [ ] Comprehensive error handling
- [ ] Logging and monitoring
- [ ] Security enhancements
- [ ] CI/CD pipeline setup

## 🙏 Acknowledgments

- LinkedIn API for social media integration
- OpenRouter, Together AI, and Hugging Face for AI services
- FastAPI community for excellent framework
- React and TypeScript communities
- All open-source contributors and libraries used

---

<p align="center">
  Built with ❤️ for LinkedIn marketers and content creators
</p>