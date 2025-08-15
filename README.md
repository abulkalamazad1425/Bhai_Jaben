# RideSharingApp - Uber Clone 🚗

A comprehensive ride-sharing application backend built with FastAPI, featuring real-time ride matching, payment processing, and rating systems.

## 🚀 Project Overview

This is a full-featured Uber-like ride-sharing platform backend that provides all the essential functionalities needed for a modern ride-sharing service. Built with FastAPI for high performance and scalability, it includes real-time communication, secure payment processing, and a comprehensive rating system.

## 📁 Project Structure

```
Backend/
├── README.md
├── script.fish                 # Fish shell script for environment setup
├── main.py                     # FastAPI application entry point
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
│
├── auth/                       # 🔐 Authentication module
│   ├── __init__.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── login_service.py    # User authentication logic
│   │   └── token_service.py    # JWT token management
│   ├── schemas.py              # Auth-related Pydantic models
│   └── routes.py               # Authentication endpoints
│
├── users/                      # 👥 User management module
│   ├── __init__.py
│   ├── service.py              # User business logic
│   ├── schemas.py              # User Pydantic models
│   ├── routes.py               # User endpoints
│   └── repositories/
│       ├── __init__.py
│       └── user_repository.py  # User data access layer
│
├── drivers/                    # 🚗 Driver management module
│   ├── __init__.py
│   ├── service.py              # Driver business logic
│   ├── schemas.py              # Driver Pydantic models
│   ├── routes.py               # Driver endpoints
│   └── repositories/
│       ├── __init__.py
│       └── driver_repository.py # Driver data access layer
│
├── rides/                      # 🛣️ Ride management module
│   ├── __init__.py
│   ├── service.py              # Ride business logic
│   ├── schemas.py              # Ride Pydantic models
│   ├── routes.py               # Ride endpoints
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── ride_repository.py  # Ride data access
│   │   └── rating_repository.py # Rating data access
│   ├── use_cases/
│   │   ├── __init__.py
│   │   └── ride_use_cases.py   # Business use cases
│   ├── domain/
│   │   ├── __init__.py
│   │   └── services.py         # Domain services (LocationService)
│   └── websocket/
│       ├── __init__.py
│       └── connection_manager.py # WebSocket management
│
├── payments/                   # 💳 Payment processing module
│   ├── __init__.py
│   ├── service.py              # Payment business logic
│   ├── schemas.py              # Payment Pydantic models
│   ├── routes.py               # Payment endpoints
│   ├── config.py               # Payment configuration
│   ├── database_config.py      # Database configuration
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── payment_repository.py # Payment data access
│   └── services/
│       ├── __init__.py
│       └── sslcommerz_service.py # SSLCommerz integration
│
└── database/                   # 🗄️ Database configuration
    ├── __init__.py
    ├── connection.py           # Database connection setup
    └── migrations/             # Database migration scripts
        ├── 001_create_users.sql
        ├── 002_create_drivers.sql
        ├── 003_create_rides.sql
        ├── 004_create_payments.sql
        └── 005_create_ratings.sql
```

## ✨ Features

### 🔐 Authentication & Authorization
- JWT-based authentication with secure token management
- Role-based access control (Users, Drivers, Admins)
- Secure password hashing using bcrypt
- Token refresh mechanism for continuous sessions
- Multi-device login support

### 👥 User Management
- User registration and profile management
- Email verification for account security
- Profile photo upload with secure storage
- User preferences and settings
- Account deletion and data privacy

### 🚗 Driver Management
- Driver registration with document verification
- Vehicle information management (make, model, license plate)
- Driver status tracking (online/offline/busy)
- Real-time driver location updates
- Driver performance analytics
- Document upload and verification system

### 🛣️ Ride Management
- Real-time ride creation and matching
- Location-based driver discovery using geospatial queries
- Comprehensive ride status tracking (pending → matched → ongoing → completed)
- Detailed ride history and analytics
- Dynamic distance and fare calculation
- Ride cancellation with policies
- Estimated time of arrival (ETA) calculation

### ⭐ Rating & Review System
- Bidirectional rating system (users rate drivers, drivers rate users)
- Detailed rating comments and feedback
- Average rating calculation and display
- Rating history and analytics
- Quality control and moderation

### 💳 Payment Processing
- Multiple payment methods (Cash, Online payments)
- SSLCommerz payment gateway integration for secure online transactions
- Real-time payment processing with instant confirmations
- Comprehensive payment history and receipts
- Automatic payment status synchronization
- Refund processing capabilities
- Payment failure handling and retry mechanisms

### 🔄 Real-time Features
- WebSocket connections for instant updates
- Real-time ride status notifications
- Live driver location tracking
- Instant messaging between users and drivers
- Push notifications for important events

## 🛠️ Technology Stack

- **Framework**: FastAPI (Python 3.8+)
- **Database**: Supabase (PostgreSQL with real-time capabilities)
- **Authentication**: JWT tokens with HS256 algorithm
- **Payment Gateway**: SSLCommerz (supports all major payment methods in Bangladesh)
- **Real-time Communication**: WebSockets
- **Validation**: Pydantic models for type safety
- **HTTP Client**: Requests library
- **Environment Management**: Python virtual environment
- **API Documentation**: Automatic OpenAPI/Swagger documentation

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- PostgreSQL database or Supabase account
- SSLCommerz merchant account (for payment processing)
- Git for version control

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/RideSharingApp_UberClone.git
   cd RideSharingApp_UberClone/Backend
   ```

2. **Set up virtual environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Linux/Mac:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Edit .env file with your configuration
   nano .env
   ```

5. **Set up database**
   ```bash
   # Run migration scripts in order
   # Execute SQL files in database/migrations/ folder
   ```

6. **Run the application**
   ```bash
   # Using fish shell script
   ./script.fish
   
   # Or directly with uvicorn
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Access the application**
   - API Documentation: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc

## ⚙️ Environment Configuration

Create a `.env` file in the Backend directory with the following variables:

```env
# Database Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key

# JWT Configuration
SECRET_KEY=your_super_secret_jwt_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# SSLCommerz Payment Gateway
SSLCOMMERZ_STORE_ID=your_sslcommerz_store_id
SSLCOMMERZ_STORE_PASSWORD=your_sslcommerz_store_password
SSLCOMMERZ_SANDBOX_URL=https://sandbox.sslcommerz.com/gwprocess/v4/api.php
SSLCOMMERZ_VALIDATION_URL=https://sandbox.sslcommerz.com/validator/api/validationserverAPI.php

# Application Settings
APP_NAME=RideSharing App
APP_VERSION=1.0.0
DEBUG=True
ENVIRONMENT=development

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# File Upload Settings
MAX_FILE_SIZE=5242880  # 5MB
ALLOWED_IMAGE_TYPES=jpg,jpeg,png,gif
```

## 📚 API Documentation

### Authentication Endpoints
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - User logout
- `GET /auth/verify-email` - Email verification

### User Management Endpoints
- `GET /users/profile` - Get current user profile
- `PUT /users/profile` - Update user profile
- `POST /users/upload-photo` - Upload profile photo
- `DELETE /users/account` - Delete user account
- `GET /users/settings` - Get user settings
- `PUT /users/settings` - Update user settings

### Driver Management Endpoints
- `POST /drivers/register` - Driver registration
- `GET /drivers/profile` - Get driver profile
- `PUT /drivers/profile` - Update driver profile
- `PUT /drivers/status` - Update driver status (online/offline)
- `POST /drivers/location` - Update driver location
- `GET /drivers/nearby` - Get nearby drivers
- `POST /drivers/documents` - Upload driver documents

### Ride Management Endpoints
- `POST /rides/create` - Create new ride request
- `GET /rides/pending` - Get pending rides (for drivers)
- `POST /rides/{id}/apply` - Apply for a ride (driver)
- `POST /rides/{id}/select-driver` - Select driver for ride (user)
- `POST /rides/{id}/start` - Start the ride
- `POST /rides/{id}/complete` - Complete the ride
- `GET /rides/my-rides` - Get user's ride history
- `GET /rides/{id}/details` - Get detailed ride information
- `POST /rides/{id}/cancel` - Cancel a ride

### Rating System Endpoints
- `POST /rides/rate` - Rate a completed ride
- `GET /rides/{id}/ratings` - Get ride ratings
- `GET /rides/my-completed` - Get completed rides with ratings
- `GET /ratings/user/{id}` - Get user rating summary
- `GET /ratings/driver/{id}` - Get driver rating summary

### Payment Endpoints
- `POST /payment/cash/{ride_id}` - Process cash payment
- `POST /payment/online/{ride_id}` - Initiate online payment
- `GET /payment/status/{ride_id}` - Get payment status
- `POST /payment/success` - Payment success callback
- `POST /payment/failed` - Payment failure callback
- `POST /payment/cancel` - Payment cancellation callback
- `GET /payment/history` - Get payment history

## 🗄️ Database Schema

### Core Tables

**users**
- Basic user information, authentication data, and preferences

**drivers**
- Driver-specific information, vehicle details, and verification status

**rides**
- Ride requests, status tracking, and fare information

**ride_applications**
- Driver applications for specific rides

**payments**
- Payment records and transaction details

**ride_ratings**
- User and driver ratings with comments

### Key Relationships
- Users can create multiple rides (1:N)
- Drivers can be assigned to multiple rides (1:N)
- Each ride has one payment record (1:1)
- Each ride can have multiple ratings (1:N)
- Each user/driver can have multiple ratings (1:N)

## 🏗️ Architecture Patterns

### Repository Pattern
- **Separation of Concerns**: Data access logic separated from business logic
- **Testability**: Easy to mock repositories for unit testing
- **Flexibility**: Easy to switch between different data sources

### Service Layer Pattern
- **Business Logic Encapsulation**: All business rules in service classes
- **Coordination**: Services coordinate between repositories and external services
- **Reusability**: Business logic can be reused across different endpoints

### Use Case Pattern
- **Complex Operations**: Multi-step business operations as use cases
- **Single Responsibility**: Each use case handles one specific business scenario
- **Testing**: Easy to test complex business flows

### Domain-Driven Design
- **Clear Boundaries**: Separation between domain logic and infrastructure
- **Domain Services**: Business rules that don't belong to entities
- **Value Objects**: Immutable objects representing domain concepts

## 🔒 Security Features

- **Password Security**: Bcrypt hashing with salt
- **JWT Security**: Secure token generation and validation
- **Input Validation**: Comprehensive Pydantic model validation
- **SQL Injection Prevention**: Parameterized queries and ORM usage
- **CORS Configuration**: Proper cross-origin request handling
- **Rate Limiting**: API rate limiting capabilities
- **File Upload Security**: File type and size validation
- **Environment Variables**: Sensitive data stored securely

## 🧪 Testing

Run tests using pytest:

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

## 🚀 Deployment

### Production Setup

1. **Environment Configuration**
   ```bash
   # Set production environment variables
   export ENVIRONMENT=production
   export DEBUG=False
   ```

2. **Database Migration**
   ```bash
   # Run production migrations
   python -m database.migrations
   ```

3. **Production Server**
   ```bash
   # Using Gunicorn for production
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📊 Monitoring & Analytics

- **Health Check Endpoint**: `/health` for system monitoring
- **Logging Configuration**: Structured logging with different levels
- **Performance Metrics**: Built-in FastAPI metrics and monitoring

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with proper tests
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add tests for new functionality
- Update documentation for API changes
- Use type hints where applicable
- Write descriptive commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support & Documentation

- **API Documentation**: Available at `/docs` when running the server
- **Issues**: Report bugs and request features via GitHub Issues
- **Wiki**: Detailed documentation in the project wiki
- **Email**: bsse1452@iit.du.ac.bd ,bsse1425@iit.du.ac.bd ,bsse1418@iit.du.ac.bd

## 🔮 Future Enhancements

- [ ] Advanced route optimization
- [ ] Machine learning for demand prediction
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Integration with mapping services
- [ ] Push notification system
- [ ] Loyalty program features
- [ ] Corporate account management

## 🛡️ Security Considerations

- Always use HTTPS in production
- Regularly update dependencies
- Implement proper rate limiting
- Use environment variables for sensitive data
- Regular security audits and penetration testing
- Implement proper logging and monitoring

## 📈 Performance Optimization

- Database indexing on frequently queried fields
- Connection pooling for database connections
- Caching frequently accessed data
- Async/await patterns for non-blocking operations
- Background tasks for heavy operations

## 🌍 Internationalization

The application is designed to support multiple languages and regions:
- Configurable currency settings
- Localized date and time formats
- Multi-language error messages
- Regional payment gateway support

---

Built with ❤️ using FastAPI and modern Python development practices

⭐ **If you find this project useful, please consider giving it a star!**