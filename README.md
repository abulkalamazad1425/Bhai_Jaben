# RideSharingApp_UberClone

A comprehensive ride-sharing backend built with FastAPI, featuring real-time ride matching, payment processing, and rating systems.

---

## 🚀 Overview

This project is a full-featured Uber-like ride-sharing backend. It supports user and driver management, ride creation and matching, real-time notifications via WebSocket, secure payment processing (SSLCommerz), and a robust rating system.

---

## 📁 Project Structure

```
Backend/
│
├── main.py                  # FastAPI application entry point
├── requirements.txt         # Python dependencies
├── script.fish              # Environment setup script
│
├── auth/                    # Authentication & registration
│   ├── database_config.py
│   ├── router.py
│   ├── schemas.py
│   └── services/
│       ├── auth_service.py
│       ├── login_service.py
│       └── register_service.py
│
├── users/                   # User profile management
│   ├── database_config.py
│   ├── router.py
│   ├── schemas.py
│   └── service.py
│
├── drivers/                 # Driver profile management
│   ├── database_config.py
│   ├── router.py
│   ├── schemas.py
│   └── service.py
│
├── rides/                   # Ride management & matching
│   ├── database_config.py
│   ├── domain/
│   │   └── services.py
│   ├── models/
│   │   └── entities.py
│   ├── repositories/
│   │   ├── rating_repository.py
│   │   └── ride_repository.py
│   ├── router.py
│   ├── schemas.py
│   ├── service.py
│   ├── use_cases/
│   │   └── ride_use_cases.py
│   └── websocket/
│       ├── connection_manager.py
│       └── router.py
│
├── payments/                # Payment processing (cash & SSLCommerz)
│   ├── config.py
│   ├── database_config.py
│   ├── repositories/
│   │   └── payment_repository.py
│   ├── router.py
│   ├── schemas.py
│   ├── service.py
│   └── services/
│       └── sslcommerz_service.py
│
├── db/                      # Database client abstraction
│   ├── database.py
│   └── supabase_client.py
│
├── shared/                  # Shared configs/utilities
│   └── config.py
│
├── sql_query/               # SQL migration scripts
│   └── migrations/
│       ├── create_users.sql
│       ├── create_drivers_profile.sql
│       ├── ride.sql
│       └── payment.sql
│
└── admin/                   # Admin dashboard & reporting
    ├── dashboard.py
    ├── drivers.py
    ├── payments.py
    ├── report.py
    ├── rides.py
    ├── router.py
    └── users.py

Frontend/
├── dummy.js
└── lib/
```

---

## ✨ Features

- **Authentication & Authorization:** JWT-based, role-based access (rider/driver), secure registration and login.
- **User Management:** Profile view/update, uniqueness checks for email/phone.
- **Driver Management:** Driver profile, vehicle info, approval status.
- **Ride Management:** Create rides, apply for rides, select driver, start/complete/cancel rides.
- **Real-time Updates:** WebSocket notifications for ride status, applications, driver location.
- **Payment Processing:** Cash and SSLCommerz online payments, payment status tracking.
- **Rating System:** Bidirectional ratings (user ↔ driver), rating summaries, comments.
- **Admin Tools:** Dashboard, reporting, user/driver/payment management.

---

## 🛠️ Technology Stack

- **Framework:** FastAPI (Python)
- **Database:** Supabase (PostgreSQL)
- **Payment Gateway:** SSLCommerz
- **Real-time:** WebSockets
- **Validation:** Pydantic models
- **Environment:** Python-dotenv, .env file

---

## ⚙️ Setup & Usage

1. **Clone the repository**
2. **Set up virtual environment**
3. **Install dependencies:**  
   `pip install -r Backend/requirements.txt`
4. **Configure environment variables:**  
   Create `.env` in `Backend/` with Supabase and SSLCommerz credentials.
5. **Run database migrations:**  
   Use SQL files in `Backend/sql_query/migrations/`
6. **Start the server:**  
   `python Backend/main.py`
7. **Access API docs:**  
   [http://localhost:8002/docs](http://localhost:8002/docs)

---

## 🗄️ Database Schema

- **users:** User info, authentication, role
- **driver_profiles:** Driver license, vehicle info, approval
- **rides:** Ride requests, status, fare, ratings
- **ride_applications:** Driver applications for rides
- **payments:** Payment records, transaction details
- **ride_ratings:** Ratings and comments for rides

---

## 🔗 API Endpoints

> All endpoints are available under `/docs` for interactive testing.

### Authentication
- `POST /auth/register` – Register a new user/driver
- `POST /auth/login` – Login and receive JWT token

### Users
- `GET /users/me` – Get current user profile
- `PUT /users/update` – Update user profile

### Drivers
- `GET /drivers/me` – Get current driver profile
- `PUT /drivers/update` – Update driver profile

### Rides
- `POST /rides/create` – Create a new ride request
- `GET /rides/available` – List available rides
- `POST /rides/apply` – Driver applies for a ride
- `POST /rides/select_driver` – Rider selects a driver
- `POST /rides/start` – Start a ride
- `POST /rides/complete` – Complete a ride
- `POST /rides/cancel` – Cancel a ride

### WebSocket
- `/rides/ws` – Real-time ride updates and notifications

### Payments
- `POST /payments/initiate` – Initiate payment (cash/SSLCommerz)
- `GET /payments/status` – Check payment status

### Ratings
- `POST /rides/rate` – Submit a rating for a ride
- `GET /rides/ratings` – Get ratings for a ride/user/driver

### Admin
- `GET /admin/dashboard` – Admin dashboard overview
- `GET /admin/users` – Manage users
- `GET /admin/drivers` – Manage drivers
- `GET /admin/rides` – Manage rides
- `GET /admin/payments` – Manage payments
- `GET /admin/report` – Generate reports

---

## 🔒 Security

- Password hashing
- JWT tokens
- Input validation
- Role checks
- Secure payment callbacks

---

## 🤝 Contributing

- Fork & PRs welcome
- Follow PEP8, use type hints
- Add tests for new features

---

## 🆘 Support

- API docs: `/docs`
- Issues: GitHub
- Email: support@ridesharing-app.com

---

## 🔮 Future Enhancements

- Advanced route optimization
- Demand prediction (ML)
- Multi-language support
- Analytics dashboard
- Push notifications
- Loyalty programs

---

Built with ❤️ using FastAPI and modern Python practices.

⭐ If you find this project useful, please give
