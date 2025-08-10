# Ancient India Blog Website

A Flask-based blog website showcasing ancient Indian architecture, sculptures, and sciences.

## Features

- **Blog Management**: Write, edit, and manage blog posts with image uploads
- **Categories**: Organize content by architecture, sculptures, and sciences
- **Image Support**: Drag & drop image uploads with captions
- **Analytics**: Track page views and visitor statistics
- **Mobile Responsive**: Optimized for all device sizes
- **Admin Panel**: Secure admin interface for content management

## Local Development

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Flask application:**
   ```bash
   python app.py
   ```

3. **Access the website:**
   - Main site: http://localhost:5000
   - Admin panel: http://localhost:5000/admin
   - Write blog: http://localhost:5000/blog

## Vercel Deployment

This application is configured for deployment on Vercel.

### Prerequisites

1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. Login to Vercel:
   ```bash
   vercel login
   ```

### Deploy to Vercel

1. **Deploy from your project directory:**
   ```bash
   vercel
   ```

2. **Follow the prompts:**
   - Link to existing project or create new
   - Set project name
   - Confirm deployment settings

3. **For production deployment:**
   ```bash
   vercel --prod
   ```

### Important Notes for Vercel

- **File Storage**: Blog posts and images are stored in `/tmp` directory on Vercel (serverless)
- **Database**: SQLite database is recreated on each function invocation
- **Persistence**: Data is not persistent between deployments - consider using external databases for production
- **Image Storage**: Images are stored temporarily - consider using cloud storage (AWS S3, Cloudinary) for production

### Environment Variables

No environment variables are required for basic deployment.

## Project Structure

```
├── app.py              # Main Flask application
├── vercel.json         # Vercel configuration
├── requirements.txt    # Python dependencies
├── runtime.txt         # Python version specification
├── templates/          # HTML templates
│   ├── index.html      # Homepage
│   ├── blog.html       # Blog writing interface
│   ├── blogs.html      # Public blog viewing
│   ├── admin.html      # Admin dashboard
│   ├── architecture.html # Architecture page
│   ├── sculpture.html  # Sculpture page
│   └── sciences.html   # Sciences page
├── static/             # Static assets
│   └── images/         # Blog images
└── blogs/              # Blog post JSON files
```

## API Endpoints

- `GET /api/blogs` - Get all blog posts
- `GET /api/blogs/<id>` - Get specific blog post
- `POST /api/blogs` - Create/update blog post
- `DELETE /api/blogs/<id>` - Delete blog post
- `GET /api/analytics/*` - Analytics endpoints

## Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLite
- **Deployment**: Vercel
- **Image Handling**: Base64 encoding/decoding

## License

This project is open source and available under the MIT License.
