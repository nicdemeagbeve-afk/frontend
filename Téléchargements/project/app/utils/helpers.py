import os
import secrets
from PIL import Image
from flask import url_for, current_app
from functools import wraps

def save_image(image_file, folder='uploads'):
    """Save uploaded image and return filename"""
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(image_file.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static', folder, picture_fn)
    
    # Resize image if needed
    output_size = (800, 800)
    i = Image.open(image_file)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    return picture_fn

def allowed_file(filename, allowed_extensions=None):
    """Check if file extension is allowed"""
    if allowed_extensions is None:
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Implement admin check logic
        # For now, just pass through
        return f(*args, **kwargs)
    return decorated_function

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"