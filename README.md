# 🚀 FastAPI MVC App

A robust and scalable FastAPI web application following the **MVC design pattern**, featuring authentication, post management, and Redis caching.

---

## 📌 Features
- ✅ **JWT-based Authentication** (Access & Refresh Tokens)
- ✅ **Secure User Registration & Login**
- ✅ **Redis Caching for Posts & Users**
- ✅ **Database ORM using SQLAlchemy**
- ✅ **Blacklisting JWT Tokens**
- ✅ **Efficient Routing & Dependency Injection**
- ✅ **Pydantic-based Input Validation**

---

## 📦 Installation & Setup
### 1️⃣ Clone the Repository
```sh
git clone https://github.com/NazarZnet/fastapi-mvc-app.git
cd fastapi-mvc-app
```

### 2️⃣ Set Up Virtual Environment
Using **Poetry**:
```sh
poetry install
```
or using **pip & venv**:
```sh
python -m venv venv
source venv/bin/activate  # (Mac/Linux)
venv\Scripts\activate     # (Windows)
pip install -r requirements.txt
```

### 3️⃣ Configure Environment Variables
Create a **`.env`** file in the project root:
```ini
SECRET_KEY=your_secret_key
REFRESH_SECRET_KEY=your_refresh_secret_key
DATABASE_URL=sqlite:///./test.db
REDIS_HOST=localhost
REDIS_PORT=6379
```

### 4️⃣ Configure App (Optional)
Open `config.py` to chnage additional configuration


---

## 🚀 Running the Application
### **Start the FastAPI Server**
```sh
poetry run uvicorn app:app --reload
```
or using `pip`:
```sh
uvicorn app:app --reload
```

- Open your browser and go to:  
  **http://127.0.0.1:8000/docs** for interactive API documentation (Swagger UI)  
  **http://127.0.0.1:8000/redoc** for alternative API docs  

---

## 📌 API Documentation

### 📝 **User Authentication**
| Endpoint       | Method | Description |
|---------------|--------|-------------|
| `/signup`     | `POST` | Register a new user |
| `/login`      | `POST` | Login and get tokens |
| `/logout`     | `POST` | Logout and blacklist token |
| `/refresh`    | `POST` | Refresh access token |

### 📝 **Post Management**
| Endpoint       | Method  | Description |
|---------------|---------|-------------|
| `/posts`      | `POST`  | Create a new post (Auth Required) |
| `/posts`      | `GET`   | Retrieve all user posts (Auth Required, Cached) |
| `/posts/{post_id}` | `DELETE` | Delete a user post (Auth Required) |


---

## 🔹 Environment Variables
| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | JWT Secret Key |
| `REFRESH_SECRET_KEY` | JWT Refresh Token Key |
| `DATABASE_URL` | Database connection string |
| `REDIS_HOST` | Redis server hostname |
| `REDIS_PORT` | Redis port number |


---

## 📜 License
This project is open-source and available under the **MIT License**.

---

## 👨‍💻 Contributors
- **Nazar Znetyniak** - _Project Maintainer_
- Feel free to contribute via pull requests! 🚀