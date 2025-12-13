"""
Unit tests for Image Resizer API
Minimum 3 tests per module as required by project
"""
import unittest
import io
from PIL import Image
import json
from app import app, stats


class TestHealthEndpoints(unittest.TestCase):
    """Test suite for health and version endpoints"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
    
    def test_health_endpoint_returns_healthy_status(self):
        """Test /health endpoint returns correct status"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('timestamp', data)
        self.assertIn('environment', data)
    
    def test_version_endpoint_returns_version(self):
        """Test /api/version endpoint returns version info"""
        response = self.client.get('/api/version')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('version', data)
        self.assertEqual(data['service'], 'image-resizer-api')
        self.assertIn('environment', data)
    
    def test_stats_endpoint_returns_statistics(self):
        """Test /api/stats endpoint returns usage stats"""
        response = self.client.get('/api/stats')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('stats', data)
        self.assertIn('uptime_seconds', data)
        self.assertIn('total_requests', data['stats'])


class TestRootEndpoint(unittest.TestCase):
    """Test suite for root endpoint"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
    
    def test_root_endpoint_returns_html(self):
        """Test / endpoint returns HTML frontend"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<!DOCTYPE html>', response.data)
        self.assertIn(b'Image Resizer', response.data)
    
    def test_root_endpoint_includes_css(self):
        """Test frontend includes CSS link"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'/static/style.css', response.data)
    
    def test_root_endpoint_includes_js(self):
        """Test frontend includes JavaScript"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'/static/app.js', response.data)


class TestImageResize(unittest.TestCase):
    """Test suite for image resize functionality"""
    
    def setUp(self):
        """Set up test client and create test image"""
        self.app = app
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
        
        # Create a test image
        self.test_image = Image.new('RGB', (800, 600), color='red')
        self.image_buffer = io.BytesIO()
        self.test_image.save(self.image_buffer, format='PNG')
        self.image_buffer.seek(0)
    
    def test_resize_endpoint_requires_image_file(self):
        """Test /api/resize returns error when no image provided"""
        response = self.client.post('/api/resize')
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('No image file provided', data['error'])
    
    def test_resize_endpoint_successfully_resizes_image(self):
        """Test /api/resize successfully resizes an image"""
        data = {
            'image': (self.image_buffer, 'test.png'),
            'width': '200',
            'height': '150'
        }
        
        response = self.client.post(
            '/api/resize',
            data=data,
            content_type='multipart/form-data'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'image/png')
    
    def test_resize_endpoint_validates_dimensions(self):
        """Test /api/resize validates width and height parameters"""
        # Reset buffer
        self.image_buffer.seek(0)
        
        data = {
            'image': (self.image_buffer, 'test.png'),
            'width': '-100',  # Invalid negative width
            'height': '150'
        }
        
        response = self.client.post(
            '/api/resize',
            data=data,
            content_type='multipart/form-data'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('Invalid dimensions', data['error'])
    
    def test_resize_endpoint_rejects_oversized_dimensions(self):
        """Test /api/resize rejects dimensions that are too large"""
        self.image_buffer.seek(0)
        
        data = {
            'image': (self.image_buffer, 'test.png'),
            'width': '10000',  # Too large
            'height': '150'
        }
        
        response = self.client.post(
            '/api/resize',
            data=data,
            content_type='multipart/form-data'
        )
        
        self.assertEqual(response.status_code, 400)


class TestImageInfo(unittest.TestCase):
    """Test suite for image info functionality"""
    
    def setUp(self):
        """Set up test client and create test image"""
        self.app = app
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
        
        # Create a test image
        self.test_image = Image.new('RGB', (800, 600), color='blue')
        self.image_buffer = io.BytesIO()
        self.test_image.save(self.image_buffer, format='PNG')
        self.image_buffer.seek(0)
    
    def test_info_endpoint_requires_image_file(self):
        """Test /api/info returns error when no image provided"""
        response = self.client.post('/api/info')
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_info_endpoint_returns_image_metadata(self):
        """Test /api/info returns correct image information"""
        data = {
            'image': (self.image_buffer, 'test.png')
        }
        
        response = self.client.post(
            '/api/info',
            data=data,
            content_type='multipart/form-data'
        )
        
        self.assertEqual(response.status_code, 200)
        
        result = json.loads(response.data)
        self.assertEqual(result['width'], 800)
        self.assertEqual(result['height'], 600)
        self.assertEqual(result['format'], 'PNG')
    
    def test_info_endpoint_includes_file_size(self):
        """Test /api/info includes file size in response"""
        self.image_buffer.seek(0)
        
        data = {
            'image': (self.image_buffer, 'test.png')
        }
        
        response = self.client.post(
            '/api/info',
            data=data,
            content_type='multipart/form-data'
        )
        
        result = json.loads(response.data)
        self.assertIn('file_size_bytes', result)
        self.assertGreater(result['file_size_bytes'], 0)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)