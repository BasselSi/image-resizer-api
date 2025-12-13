"""
Image Resizer API - Simple Data Processing Application
Accepts images, processes them (resize), and returns the result
"""
from flask import Flask, request, jsonify, send_file, render_template
from PIL import Image
import io
import os
import logging
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration from environment variables
APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
APP_ENV = os.getenv('APP_ENV', 'development')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
MAX_IMAGE_SIZE = int(os.getenv('MAX_IMAGE_SIZE', 10 * 1024 * 1024))  # 10MB default

# Set log level from environment
logger.setLevel(LOG_LEVEL)

# Statistics counter
stats = {
    'total_requests': 0,
    'successful_resizes': 0,
    'failed_resizes': 0,
    'start_time': datetime.now().isoformat()
}


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint required by project
    Returns: JSON with status
    """
    stats['total_requests'] += 1
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'environment': APP_ENV
    }), 200


@app.route('/', methods=['GET'])
def index():
    """
    Serve the web UI
    Returns: HTML page
    """
    return render_template('index.html')


@app.route('/api/version', methods=['GET'])
def version():
    """
    Version endpoint required by project
    Returns: JSON with version info
    """
    stats['total_requests'] += 1
    return jsonify({
        'version': APP_VERSION,
        'service': 'image-resizer-api',
        'environment': APP_ENV
    }), 200


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    Statistics endpoint to monitor API usage
    Returns: JSON with usage statistics
    """
    stats['total_requests'] += 1
    uptime = (datetime.now() - datetime.fromisoformat(stats['start_time'])).total_seconds()
    
    return jsonify({
        'stats': stats,
        'uptime_seconds': uptime
    }), 200


@app.route('/api/resize', methods=['POST'])
def resize_image():
    """
    Main processing endpoint - resizes images
    Accepts: multipart/form-data with 'image' file and optional 'width' and 'height'
    Returns: Resized image or error message
    """
    stats['total_requests'] += 1
    
    try:
        # Validate request has file
        if 'image' not in request.files:
            logger.warning("No image file in request")
            stats['failed_resizes'] += 1
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        
        # Validate file is not empty
        if file.filename == '':
            logger.warning("Empty filename")
            stats['failed_resizes'] += 1
            return jsonify({'error': 'No file selected'}), 400
        
        # Get resize dimensions (default to 300x300)
        width = request.form.get('width', 300, type=int)
        height = request.form.get('height', 300, type=int)
        
        # Validate dimensions
        if width <= 0 or height <= 0 or width > 5000 or height > 5000:
            logger.warning(f"Invalid dimensions: {width}x{height}")
            stats['failed_resizes'] += 1
            return jsonify({'error': 'Invalid dimensions. Must be between 1 and 5000'}), 400
        
        # Read and process image
        image_data = file.read()
        
        # Check file size
        if len(image_data) > MAX_IMAGE_SIZE:
            logger.warning(f"Image too large: {len(image_data)} bytes")
            stats['failed_resizes'] += 1
            return jsonify({'error': f'Image too large. Max size: {MAX_IMAGE_SIZE} bytes'}), 400
        
        # Open image with PIL
        image = Image.open(io.BytesIO(image_data))
        original_size = image.size
        
        logger.info(f"Resizing image from {original_size} to {width}x{height}")
        
        # Resize image
        resized_image = image.resize((width, height), Image.Resampling.LANCZOS)
        
        # Save to bytes buffer
        buffer = io.BytesIO()
        image_format = image.format or 'PNG'
        resized_image.save(buffer, format=image_format)
        buffer.seek(0)
        
        stats['successful_resizes'] += 1
        logger.info(f"Successfully resized image from {original_size} to {width}x{height}")
        
        return send_file(
            buffer,
            mimetype=f'image/{image_format.lower()}',
            as_attachment=True,
            download_name=f'resized_{file.filename}'
        )
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        stats['failed_resizes'] += 1
        return jsonify({'error': f'Failed to process image: {str(e)}'}), 500


@app.route('/api/info', methods=['POST'])
def image_info():
    """
    Get information about an image without processing
    Accepts: multipart/form-data with 'image' file
    Returns: JSON with image metadata
    """
    stats['total_requests'] += 1
    
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read image
        image_data = file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # Extract metadata
        info = {
            'filename': file.filename,
            'format': image.format,
            'mode': image.mode,
            'size': image.size,
            'width': image.width,
            'height': image.height,
            'file_size_bytes': len(image_data)
        }
        
        logger.info(f"Retrieved info for image: {file.filename}")
        return jsonify(info), 200
        
    except Exception as e:
        logger.error(f"Error getting image info: {str(e)}")
        return jsonify({'error': f'Failed to get image info: {str(e)}'}), 500


@app.route('/', methods=['GET'])
def root():
    """
    Root endpoint with API documentation
    """
    stats['total_requests'] += 1
    return jsonify({
        'service': 'Image Resizer API',
        'version': APP_VERSION,
        'endpoints': {
            'GET /health': 'Health check',
            'GET /api/version': 'Get API version',
            'GET /api/stats': 'Get usage statistics',
            'POST /api/resize': 'Resize an image (multipart/form-data: image, width, height)',
            'POST /api/info': 'Get image information'
        }
    }), 200


# Graceful shutdown handling
def shutdown_handler():
    """Handle graceful shutdown"""
    logger.info("Shutting down gracefully...")
    logger.info(f"Final stats: {stats}")


if __name__ == '__main__':
    import signal
    import sys
    
    def signal_handler(sig, frame):
        shutdown_handler()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    port = int(os.getenv('PORT', 8080))
    logger.info(f"Starting Image Resizer API v{APP_VERSION} on port {port}")
    logger.info(f"Environment: {APP_ENV}")
    
    # Run app
    app.run(host='0.0.0.0', port=port, debug=(APP_ENV == 'development'))