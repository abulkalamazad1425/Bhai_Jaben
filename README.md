# RideSharingApp_UberClone

A full-stack ride sharing app (Uber clone) built with FastAPI (Python) for backend and Flutter for frontend.

---

## Project Structure

```
RideSharingApp_UberClone/
│
├── Backend/           # FastAPI backend
│   ├── main.py
│   ├── auth/
│   ├── users/
│   ├── rides/
│   ├── db/
│   ├── .env
│   └── requirements.txt
│
└── Frontend/          # Flutter frontend
    └── frontend/
        ├── lib/
        │   ├── main.dart
        │   ├── api_service.dart
        │   ├── models/
        │   │   └── ride.dart
        │   └── screens/
        │       └── home_screen.dart
        └── pubspec.yaml
```

---

## Backend Setup (FastAPI)

1. **Install dependencies:**
   ```bash
   cd Backend
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   - Edit `.env` file with your database credentials.

3. **Run the server:**
   ```bash
   python -m uvicorn main:app --reload
   ```

4. **API Docs:**
   - Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Frontend Setup (Flutter)

1. **Install Flutter:**  
   [Flutter installation guide](https://docs.flutter.dev/get-started/install)

2. **Create/Open project:**
   ```bash
   cd Frontend
   flutter create frontend
   cd frontend
   ```

3. **Install dependencies:**
   ```bash
   flutter pub add http
   ```

4. **Run the app:**
   ```bash
   flutter run
   ```
   - Choose device: Windows, Chrome, or Edge.

---

## Features

- User authentication & profile
- Ride request, status, and history
- REST API integration between frontend and backend
- Responsive UI (Flutter)

---

## Notes

- For local development, make sure backend is running before starting frontend.
- If running Flutter web, ensure FastAPI CORS is enabled:
  ```python
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```
- Update API URLs in `api_service.dart` if deploying to production.

---

## Contributing

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

---

##
