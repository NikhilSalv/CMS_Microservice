## 🔑 Authentication

JWT Authentication is handled via **SimpleJWT**.

- `POST /api/auth/register/` → Register and auto-login  
- `POST /api/auth/login/` → Obtain JWT  
- `POST /api/auth/refresh/` → Refresh JWT  

---

## 👤 Profile Endpoints

- `GET /api/profiles/me/` → Fetch own profile  
- `PUT /api/profiles/me/` → Update profile  

---

## 👫 Friendship Endpoints

- `POST /api/friendships/request/` → Send a new friend request  
- `GET /api/friendships/` → List all friendships and requests (sent + received)  
- `GET /api/friendships/received/` → List friend requests you have received  
- `POST /api/friendships/respond/{id}/` → Respond to a friend request  

---

## 👥 User Endpoints

- `GET /api/users/` → List all users (for friend searching)  

---

## 📜 API Documentation

Swagger & ReDoc are enabled:

- **Swagger UI** → [http://localhost:8000/swagger/](http://localhost:8000/swagger/)  
- **ReDoc** → [http://localhost:8000/redoc/](http://localhost:8000/redoc/)  


## 📈 Sequence Diagram – Friend Request Flow

```mermaid
sequenceDiagram
    participant U1 as User A (Requester)
    participant U2 as User B (Addressee)
    participant FE as Frontend (React)
    participant API as Identity Service (Django/DRF)
    participant DB as PostgreSQL (identity-db)
    participant RP as Redpanda (Events)

    %% --- Send Friend Request ---
    U1->>FE: Click "Send Friend Request"
    FE->>API: POST /api/friendships/request/ { addressee_id }
    API->>DB: INSERT INTO friendship (requester, addressee, status="requested")
    DB-->>API: Friendship created
    API-->>FE: 201 Created (Friend request sent)
    FE-->>U1: Show "Friend request pending"

    %% --- Respond to Friend Request ---
    U2->>FE: Click "Accept Request"
    FE->>API: POST /api/friendships/respond/{id}/ { "action": "accept" }
    API->>DB: UPDATE friendship SET status="accepted" WHERE id={id}
    DB-->>API: Update successful
    API->>RP: Emit "friendship.accepted" event
    API-->>FE: 200 OK (Friendship accepted)
    FE-->>U2: Show "You are now friends"



## 📊 Architecture Diagram

          ┌──────────────┐
          │   Frontend   │
          └──────┬───────┘
                 │
        ┌────────▼────────┐
        │ Identity Service │ (Django + DRF + JWT)
        └───────┬─────────┘
                │
    ┌───────────┼─────────────┐
    │           │             │
┌───▼───┐   ┌───▼────┐   ┌────▼────┐
│Profile│   │Friend- │   │Auth/JWT │
│ Model │   │ ship   │   │   API   │
└───┬───┘   │ Model  │   └────┬────┘
    │       └───┬────┘        │
    │           │             │
    ▼           ▼             ▼
 PostgreSQL   PostgreSQL   Redis/MinIO/Redpanda
 (identity)   (relations)   (future events/storage)
