# SpielViel API

The SpielViel API is a FastAPI application that manages board game data, retrieves it from BoardGameGeek, and uses a SQLite database. The API allows users to manage the collection and lending of games.

---

## **Project Structure**

```
spielviel-api/
├── __pycache__/          # Python cache files
├── alembic/              # Database migrations
├── env/                  # Environment files (e.g., virtual environment)
├── auth.py               # Authentication logic
├── automatic_importer.py # Automatic data imports
├── build.sh              # Optional build script
├── database.py           # Database configuration with SQLAlchemy
├── db.sqlite3            # SQLite database
├── Dockerfile            # Docker configuration file
├── fetch_and_store.py    # Fetch logic from BoardGameGeek
├── fetch_and_store_private.py # Fetch logic for private data
├── main.py               # Main API application
├── models.py             # Database models
├── requirements.txt      # Python dependencies
├── scrape_german_name_playwright.py # Additional import logic
```

---

## **Prerequisites**

- Docker (https://www.docker.com/get-started)
- Python 3.11 (if not using Docker)
- SQLite (included in the Docker setup)

---

## **Local Setup**

### 1. Clone the Repository

```bash
git clone <repository-url>
cd spielviel-api
```

### 2. Set Up Environment Variables

Create a `.env` file in the root directory with the following content:

```
BGG_USERNAME=<your_bgg_username>
BGG_PASSWORD=<your_bgg_password>
```

These variables are used to access the BoardGameGeek API.

### 3. Install Python Dependencies (Optional, if not using Docker)

Activate a virtual environment and install the dependencies:

```bash
python3 -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
pip install -r requirements.txt
```

---

## **Using Docker**

Docker is used to run the application consistently in an isolated environment.

### 1. Build the Docker Image

Build the Docker image from the `Dockerfile`:

```bash
docker build -t spielviel-api .
```

- `-t spielviel-api`: Names the Docker image `spielviel-api`.
- `.`: Indicates that the `Dockerfile` is in the current directory.

### 2. Start the Container

Start a Docker container with the image:

```bash
docker run -v spielviel-api:/app -p 8000:8000 spielviel-api
```

- `-d`: Runs the container in the background.
- `-p 8000:8000`: Maps port 8000 of the container to port 8000 on your host.
- `--env-file .env`: Passes the environment variables from the `.env` file to the container.
- `spielviel-api`: The name of the Docker image.

### 3. View Logs (Optional)

Display the logs of the running container:

```bash
docker logs <container-id>
```

### 4. Access the Container Shell (Optional)

If you need to work directly inside the container, open a shell:

```bash
docker exec -it <container-id> bash
```

Replace `<container-id>` with the ID of the container (available with `docker ps`).

---

## **Deployment on Render**

### Preparation

- Ensure a `Dockerfile` is in the root directory of your project.
- Set all environment variables in Render via the dashboard:
  - `BGG_USERNAME`
  - `BGG_PASSWORD`

### Render Setup

1. Go to https://render.com and create a new Web Service.
2. Link your GitHub repository.
3. Render automatically detects the `Dockerfile`. If not:
   - Add a `render.yaml` file:

```yaml
services:
  - type: web
    name: spielviel-api
    env: docker
    build:
      dockerfilePath: ./Dockerfile
    envVars:
      - key: BGG_USERNAME
        value: "<your_bgg_username>"
      - key: BGG_PASSWORD
        value: "<your_bgg_password>"
```

4. Start the deployment and check the logs for errors.

---

## **API Documentation**

### Key Endpoints

1. **Root Endpoint**

   - **GET /:**
     - Response: `{ "message": "Hello World" }`

2. **Get Token**

   - **POST /token:**
     - Body: `{ "username": <string>, "password": <string> }`
     - Response: `{ "access_token": <token>, "token_type": "bearer" }`

3. **List Games**

   - **GET /games:**
     - Response: List of all games in the database.

4. **Add Game**

   - **POST /create_game:**
     - Body: `{ "name": <string>, "ean": <string>, "img_url": <string>, "is_available": <bool> }`
     - Response: Added game.

5. **Fetch Collection from BoardGameGeek**
   - **POST /fetch_private_collection:**
     - Response: Collection of BoardGameGeek data.

---

## **Known Issues**

1. **Google Chrome Not Found:**

   - Ensure your `Dockerfile` correctly installs `google-chrome-stable` and `chromium-driver`.

2. **Database Persistence:**
   - SQLite stores data in the container. Use Docker volumes to persist data:

```bash
docker run -v $(pwd)/data:/app/data -p 8000:8000 spielviel-api
```

---

## **Future Improvements**

- Switch to a PostgreSQL database for scalability.
- Add tests for endpoints (e.g., with `pytest`).
- Optimize Docker and deployment workflows for CI/CD.
