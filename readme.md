# Image Moderation API Backend

This backend is a FastAPI-based service for moderating images and detecting harmful content using deep learning models. It provides authentication, image analysis, and usage logging, and stores data in MongoDB.

---

## Features

- **Image Moderation:** Upload images to detect harmful content using a transformer-based model.
- **Authentication:** Bearer token-based authentication with admin and user roles.
- **Usage Logging:** Tracks API usage per token and endpoint.
- **Admin Endpoints:** Manage tokens (create, list, delete).
- **Health Check:** Simple endpoint to verify service status.

---

## Project Structure

```
backend/
  requirements.txt
  Dockerfile
  app/
    main.py              # FastAPI app, endpoints, and startup logic
    auth_service.py      # AuthService class for token validation and usage logging
    image_analyzer.py    # ImageAnalyzer class for image moderation logic
    database/
      models.py          # Pydantic models for tokens, usage, moderation results
      mongodb.py         # MongoDB connection and helpers
docker-compose.yml
```

---

## Dependencies

All dependencies are listed in [`backend/requirements.txt`](backend/requirements.txt):

- **fastapi**: Web framework for building APIs
- **uvicorn**: ASGI server for running FastAPI
- **motor**: Async MongoDB driver
- **pymongo**: MongoDB driver
- **python-multipart**: For handling file uploads
- **Pillow**: Image processing
- **numpy**: Numerical operations
- **pydantic**: Data validation and settings management
- **python-jose[cryptography]**: JWT and cryptography for tokens
- **passlib[bcrypt]**: Password hashing
- **python-dotenv**: Environment variable management
- **transformers**: HuggingFace Transformers for image classification
- **torchvision**: PyTorch vision utilities

---

## How It Works

### 1. Authentication

- Uses Bearer tokens for authentication.
- Admin tokens can create, list, and delete tokens.
- Token validation and usage logging are handled by [`AuthService`](backend/app/auth_service.py).

### 2. Image Moderation

- `/moderate` endpoint accepts image uploads.
- Images are processed by [`ImageAnalyzer`](backend/app/image_analyzer.py) using a transformer model.
- The result includes safety categories, confidence scores, and an overall safety verdict.

### 3. Database

- MongoDB is used for storing tokens, usage logs, and moderation results.
- Async access via Motor.

### 4. Endpoints

- `POST /moderate`: Analyze an uploaded image (requires token).
- `POST /auth/tokens`: Create a new token (admin only).
- `GET /auth/tokens`: List all tokens (admin only).
- `DELETE /auth/tokens/{token}`: Delete a token (admin only).
- `GET /health`: Health check endpoint.

---

## Downloading the Project

Clone this repository (including submodules) using:
```sh
git clone --recurse-submodules https://github.com/leohum69/Image-Moderation-FastAPI
```
---


## Running the Backend

### Local Development

1. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

2. **Set up MongoDB:**
   - Ensure a MongoDB instance is running and accessible.

3. **Run the server:**
   ```sh
   python app/main.py
   ```

### Using Docker Compose

You can run the backend, frontend, and MongoDB together using Docker Compose.

1. **Build and start all services:**
   ```sh
   docker-compose up --build
   ```

   - The backend will be available at `http://localhost:7000`
   - The frontend (if present) will be at `http://localhost:3000`
   - MongoDB will be available at port `27018` on your host

2. **Stop the services:**
   ```sh
   docker-compose down
   ```

---

## Environment Variables

- Configure MongoDB connection and secrets as needed (see `.env` usage in code).
- When using Docker Compose, environment variables are set in the `docker-compose.yml` file.

---

## License

MIT License. See [LICENSE](/LICENSE) for details.

---

**Author:** Lalaleo_Chan