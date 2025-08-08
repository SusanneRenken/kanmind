# Kanban Board API (Django + DRF)

REST API for boards, tasks, and comments. Auth via DRF Token.

## Quick Start
```bash
python -m venv env
# Windows
env\Scripts\activate
# macOS/Linux
source env/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

python manage.py createsuperuser
```

## Auth
- Get a token with `/api/login/`, then send:
```
Authorization: Token <YOUR_TOKEN>
```

## Endpoints (summary)

### Auth
- `POST /api/registration/` – create user  
- `POST /api/login/` – obtain token  
- `GET  /api/email-check/?email=...` – check email (requires auth)

### Boards
- `GET  /api/boards/` – list (owner or member)  
- `POST /api/boards/` – create (owner = requester; members from payload; owner not auto-added as member)  
- `GET  /api/boards/{id}/` – details (incl. members, tasks)  
- `PATCH /api/boards/{id}/` – update title/members  
- `DELETE /api/boards/{id}/` – delete (owner only)

### Tasks
- `GET  /api/tasks/assigned-to-me/` – tasks assigned to me  
- `GET  /api/tasks/reviewing/` – tasks I review  
- `POST /api/tasks/` – create (assignee_id/reviewer_id must be board members or owner)  
- `PATCH /api/tasks/{id}/` – update (board not changeable)  
- `DELETE /api/tasks/{id}/` – delete (creator or board owner)

### Comments
- `GET  /api/tasks/{task_id}/comments/` – list  
- `POST /api/tasks/{task_id}/comments/` – create  
- `DELETE /api/tasks/{task_id}/comments/{comment_id}/` – delete (author only)

## Notes
- Default permissions: `IsAuthenticated` (except registration/login).
- Apps: `auth_app/`, `kanban_app/` each with `api/` (serializers, views, urls, permissions).
- DB: SQLite by default. Do not commit `db.sqlite3`.
