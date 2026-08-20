# Blog App

A Django blog application built while learning Django from scratch. It provides a server-rendered web interface for reading and managing posts, plus a small JSON API for programmatic post creation and updates.

## Features

- User sign-up, login, logout, and session-based authentication
- Create, edit, and delete blog posts through HTML forms
- Published and draft post states
- Public post listing with search and pagination
- View counters on published post detail pages
- JSON API for creating, reading, updating, and deleting posts
- Author-based permissions, with staff and superusers able to manage any post
- SQLite database for local development
- Automated tests for authentication, forms, pages, API mutations, search, pagination, and permissions

## Tech Stack

- Python 3.12 or newer
- Django 6.0
- SQLite
- `uv` for dependency and virtual-environment management

## Project Structure

```text
.
├── backend/
│   ├── manage.py              # Django management entry point
│   ├── db.sqlite3             # Local development database
│   ├── blog/                  # Blog application
│   └── config/                # Django project configuration
├── pyproject.toml             # Project metadata and dependencies
└── uv.lock                    # Locked dependency versions
```

## Getting Started

### Prerequisites

Install Python 3.12+ and [uv](https://docs.astral.sh/uv/).

### Install dependencies

From the project root:

```bash
uv sync
```

This creates or updates the local `.venv` and installs the dependencies from `uv.lock`.

### Apply migrations

```bash
cd backend
uv run python manage.py migrate
```

### Create an admin user (optional)

```bash
uv run python manage.py createsuperuser
```

### Start the development server

From `backend/`:

```bash
uv run python manage.py runserver
```

Open <http://127.0.0.1:8000/> in a browser. The admin site is available at <http://127.0.0.1:8000/admin/>.

If you activate the virtual environment manually, the equivalent commands use `python` instead of `uv run python`:

```bash
source .venv/bin/activate
cd backend
python manage.py runserver
```

## Web Routes

All blog routes are prefixed with `/blogs/`.

| Method | Route | Description | Authentication |
| --- | --- | --- | --- |
| GET | `/` | Home page | Public |
| GET | `/blogs/` | Published posts, search, and pagination | Public |
| GET | `/blogs/<post-id>/` | Published post detail and view counter | Public |
| GET | `/blogs/signup/` | Registration form | Public |
| GET/POST | `/blogs/login/` | Login form | Public |
| POST | `/blogs/logout/` | Log out | Required |
| GET/POST | `/blogs/create/` | Create a post | Required |
| GET | `/blogs/mine/` | List the current user’s posts | Required |
| GET/POST | `/blogs/<post-id>/edit/` | Edit a post | Author, staff, or superuser |
| GET/POST | `/blogs/<post-id>/delete/` | Delete a post | Author, staff, or superuser |

Search the public listing with a query parameter:

```text
/blogs/?q=django&page=2
```

Posts are searched by title, content, category, and author username. The listing contains six posts per page.

## JSON API

The API uses the same session authentication as the web interface. Send JSON with `Content-Type: application/json`. Post IDs are UUIDs.

### Create a post

```bash
curl -X POST http://127.0.0.1:8000/blogs/api/create/ \
	-H 'Content-Type: application/json' \
	-b cookies.txt \
	-d '{
		"title": "My first post",
		"content": "Post content goes here.",
		"category": "Django",
		"is_published": true
	}'
```

`title` and `content` are required. New posts are associated with the authenticated user.

### Read a post

```bash
curl -H 'Accept: application/json' \
	http://127.0.0.1:8000/blogs/<post-id>/
```

The detail endpoint increments the post’s view counter. Unpublished posts are not publicly readable.

### Update a post

Use `PATCH` for a partial update:

```bash
curl -X PATCH http://127.0.0.1:8000/blogs/<post-id>/ \
	-H 'Content-Type: application/json' \
	-b cookies.txt \
	-d '{"title": "Updated title"}'
```

Use `PUT` to replace the editable fields. `PUT` requires `title` and `content`.

Editable fields are `title`, `content`, `category`, and `is_published`. Only the post author, a staff user, or a superuser can update or delete a post.

### Delete a post

```bash
curl -X DELETE http://127.0.0.1:8000/blogs/<post-id>/ \
	-b cookies.txt
```

A successful delete returns HTTP `204 No Content`.

## Data Model

Each `Post` contains:

- `id`: UUID primary key
- `title`: required string, up to 200 characters
- `content`: required text
- `author`: Django user who created the post
- `category`: optional string, up to 100 characters
- `is_published`: draft/published flag, defaulting to `false`
- `views`: non-negative view count
- `created_at` and `updated_at`: automatic timestamps

## Running Tests

From the project root:

```bash
uv run python backend/manage.py test blog
```

Run Django’s checks separately when troubleshooting configuration:

```bash
uv run python backend/manage.py check
```

## Development Notes

- The default database is `backend/db.sqlite3`.
- The project currently runs with `DEBUG = True` and contains a development secret key. Do not use these settings in production.
- Before deployment, configure a secret key through the environment, set `DEBUG = False`, define `ALLOWED_HOSTS`, configure secure cookies and HTTPS, and run `collectstatic`.
- The API endpoints are intentionally lightweight Django views rather than a Django REST Framework application.
- The development server should be started from `backend/`, or given the project settings through Django’s normal command-line configuration.
