let resizedImageBlob = null;

// Load version and status on page load
async function loadAppInfo() {
    try {
        const [versionRes, healthRes] = await Promise.all([
            fetch('/api/version'),
            fetch('/health')
        ]);

        const version = await versionRes.json();
        const health = await healthRes.json();

        document.getElementById('version').textContent = version.version;
        document.getElementById('environment').textContent = version.environment;
        document.getElementById('status').textContent = health.status === 'healthy' ? '● Healthy' : '● Down';
        document.getElementById('status').className = health.status === 'healthy' ? 'stat-value status-healthy' : 'stat-value';
    } catch (error) {
        console.error('Failed to load app info:', error);
    }
}

// Handle file selection
document.getElementById('imageInput').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        document.getElementById('fileName').textContent = file.name;
        
        // Display original image preview
        const reader = new FileReader();
        reader.onload = function(e) {
            const img = document.getElementById('originalImage');
            img.src = e.target.result;
            
            // Get image dimensions
            img.onload = function() {
                document.getElementById('originalInfo').textContent = 
                    `${img.naturalWidth} × ${img.naturalHeight} px`;
            };
        };
        reader.readAsDataURL(file);
    }
});

// Handle form submission
document.getElementById('uploadForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('imageInput');
    const width = document.getElementById('width').value;
    const height = document.getElementById('height').value;
    const errorDiv = document.getElementById('error');
    const resultsDiv = document.getElementById('results');
    const resizeBtn = document.getElementById('resizeBtn');
    const btnText = resizeBtn.querySelector('.btn-text');
    const spinner = resizeBtn.querySelector('.spinner');
    
    // Reset error and results
    errorDiv.style.display = 'none';
    resultsDiv.style.display = 'none';
    
    if (!fileInput.files[0]) {
        showError('Please select an image file');
        return;
    }
    
    // Show loading state
    resizeBtn.disabled = true;
    btnText.textContent = 'Resizing...';
    spinner.style.display = 'inline-block';
    
    try {
        const formData = new FormData();
        formData.append('image', fileInput.files[0]);
        formData.append('width', width);
        formData.append('height', height);
        
        const response = await fetch('/api/resize', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to resize image');
        }
        
        const blob = await response.blob();
        resizedImageBlob = blob;
        
        // Display resized image
        const url = URL.createObjectURL(blob);
        const resizedImg = document.getElementById('resizedImage');
        resizedImg.src = url;
        
        resizedImg.onload = function() {
            document.getElementById('resizedInfo').textContent = 
                `${resizedImg.naturalWidth} × ${resizedImg.naturalHeight} px`;
            resultsDiv.style.display = 'grid';
        };
        
    } catch (error) {
        showError(error.message);
    } finally {
        resizeBtn.disabled = false;
        btnText.textContent = 'Resize Image';
        spinner.style.display = 'none';
    }
});

// Handle download
document.getElementById('downloadBtn').addEventListener('click', function() {
    if (resizedImageBlob) {
        const url = URL.createObjectURL(resizedImageBlob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'resized_image.jpg';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
});

function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

// Initialize
loadAppInfo();
