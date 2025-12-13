# Image Resizer API

![CI](https://github.com/BasselSi/image-resizer-api/actions/workflows/workflow.yml/badge.svg)
![Docker](https://img.shields.io/badge/docker-ghcr.io%2Fbasselsi%2Fimage--resizer--api-blue)

A simple yet powerful image processing API built with Flask. Accepts images, processes them (resize), and returns the result.

## 🚀 Features

- **Image Resizing**: Upload images and get them resized to custom dimensions
- **Image Info**: Get metadata about uploaded images
- **Health Checks**: Built-in health and version endpoints for monitoring
- **Statistics**: Track API usage with the `/api/stats` endpoint
- **Production Ready**: Includes graceful shutdown, logging, and error handling

## 📋 Requirements

- Python 3.9+
- Docker (for containerized deployment)
- Kubernetes cluster (for production deployment)

## 🏃 Running Locally

### Option 1: Using Python directly

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Or use gunicorn for production
gunicorn --bind 0.0.0.0:8080 --workers 2 app:app
```

### Option 2: Using Docker

```bash
# Build the Docker image
docker build -t image-resizer-api .

# Run the container
docker run -p 8080:8080 image-resizer-api

# Run with environment variables
docker run -p 8080:8080 \
  -e APP_ENV=production \
  -e LOG_LEVEL=INFO \
  image-resizer-api
```

## 🧪 Running Tests

```bash
# Install dependencies (recommended inside a venv)
pip install -r requirements.txt

# Run all tests with pytest (recommended)
python -m pytest -q app_test.py

# Or run tests with unittest directly
python app_test.py

# Run with coverage (requires pytest-cov)
python -m pytest app_test.py --cov=app --cov-report=html
```

## 📡 API Endpoints

### Health & Status

#### `GET /health`
Returns the health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-12-06T10:00:00",
  "environment": "production"
}
```

#### `GET /api/version`
Returns version information.

**Response:**
```json
{
  "version": "1.0.0",
  "service": "image-resizer-api",
  "environment": "production"
}
```

#### `GET /api/stats`
Returns API usage statistics.

**Response:**
```json
{
  "stats": {
    "total_requests": 150,
    "successful_resizes": 120,
    "failed_resizes": 5
  },
  "uptime_seconds": 3600
}
```

### Image Processing

#### `POST /api/resize`
Resize an uploaded image to specified dimensions.

**Parameters:**
- `image` (file, required): The image file to resize
- `width` (int, optional): Target width in pixels (default: 300)
- `height` (int, optional): Target height in pixels (default: 300)

**Example with curl:**
```bash
curl -X POST http://localhost:8080/api/resize \
  -F "image=@photo.jpg" \
  -F "width=500" \
  -F "height=400" \
  --output resized_photo.jpg
```

**Example with Python:**
```python
import requests

files = {'image': open('photo.jpg', 'rb')}
data = {'width': 500, 'height': 400}
response = requests.post('http://localhost:8080/api/resize', files=files, data=data)

with open('resized_photo.jpg', 'wb') as f:
    f.write(response.content)
```

#### `POST /api/info`
Get information about an uploaded image without processing it.

**Parameters:**
- `image` (file, required): The image file to analyze

**Response:**
```json
{
  "filename": "photo.jpg",
  "format": "JPEG",
  "mode": "RGB",
  "size": [1920, 1080],
  "width": 1920,
  "height": 1080,
  "file_size_bytes": 524288
}
```

## 🔧 Configuration

The application can be configured using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_VERSION` | Application version | `1.0.0` |
| `APP_ENV` | Environment (development/production) | `development` |
| `LOG_LEVEL` | Logging level (DEBUG/INFO/WARNING/ERROR) | `INFO` |
| `PORT` | Server port | `8080` |
| `MAX_IMAGE_SIZE` | Maximum upload size in bytes | `10485760` (10MB) |

## 🐳 Docker Deployment

The application includes an optimized multi-stage Dockerfile:

```bash
# Build
docker build -t image-resizer-api:latest .

# Run
docker run -d \
  --name image-resizer \
  -p 8080:8080 \
  -e APP_ENV=production \
  image-resizer-api:latest
```

## ☸️ Kubernetes Deployment

Deploy to Kubernetes using the provided manifests:

```bash
# Apply all manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n k8s-yourname
kubectl get services -n k8s-yourname

# Get service URL
kubectl get service image-resizer-service -n k8s-yourname
```

## 🔒 Security Features

- Non-root user in container
- Input validation on all endpoints
- File size limits to prevent DoS
- Dimension validation to prevent resource exhaustion
- No secrets in code (environment variables only)

## 📊 Monitoring

The application provides:
- Health check endpoint for Kubernetes probes
- Statistics endpoint for monitoring
- Structured logging for observability
- Graceful shutdown handling

## 🛠️ Development

### Project Structure

```
image-resizer-api/
├── app.py                  # Main application
├── test_app.py            # Unit tests
├── requirements.txt       # Python dependencies
├── Dockerfile             # Container image definition
├── .dockerignore          # Docker build exclusions
├── .github/
│   └── workflows/
│       └── build-test-deploy.yml  # CI/CD pipeline
├── k8s/                   # Kubernetes manifests
│   ├── namespace.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   └── configmap.yaml
└── README.md
```

### Adding New Features

1. Add your feature to `app.py`
2. Write tests in `test_app.py`
3. Update this README
4. Test locally with `python app.py`
5. Run tests with `python test_app.py`
6. Build Docker image and test
7. Push to GitHub (CI/CD will handle the rest)

## 🤝 Contributing

This is a DevOps bootcamp project. If you're working on this:

1. Follow the project requirements document
2. Write tests for all new features
3. Keep Dockerfile optimized (<500MB, preferably <200MB)
4. Update documentation as you go
5. Test the full CI/CD pipeline before submission

## 📝 License

This project is created for educational purposes as part of the DevOps Bootcamp.

## 🙋 Support

- Check logs: `docker logs <container_id>` or `kubectl logs <pod_name>`
- Review error messages carefully
- Refer to the DevOps Bootcamp troubleshooting guide
- Ask in the bootcamp Discord/Slack channel

---

**Built with ❤️ for the DevOps Bootcamp Complete Project**