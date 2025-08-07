# Netlify Functions

This directory contains serverless functions for the AI Performance Testing Suite.

## Available Functions

### 1. `hello.js`
- **Purpose:** Simple test function
- **Endpoint:** `/.netlify/functions/hello`
- **Method:** GET
- **Response:** JSON with greeting message and timestamp

### 2. `api-status.js`
- **Purpose:** Check backend connectivity
- **Endpoint:** `/.netlify/functions/api-status`
- **Method:** GET
- **Response:** Backend connection status
- **Dependencies:** axios

### 3. `contact-form.js`
- **Purpose:** Handle contact form submissions
- **Endpoint:** `/.netlify/functions/contact-form`
- **Method:** POST
- **Body:** `{ name, email, message, subject? }`
- **Response:** Success/error message

## Usage

### From Frontend
```javascript
// Check API status
fetch('/.netlify/functions/api-status')
  .then(response => response.json())
  .then(data => console.log(data));

// Submit contact form
fetch('/.netlify/functions/contact-form', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'John Doe',
    email: 'john@example.com',
    message: 'Hello!',
    subject: 'General Inquiry'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

## Environment Variables

Make sure to set these in your Netlify dashboard:
- `REACT_APP_BACKEND_URL`: Your backend URL

## Local Development

To test functions locally:
1. Install Netlify CLI: `npm install -g netlify-cli`
2. Run: `netlify dev`
3. Functions will be available at `http://localhost:8888/.netlify/functions/`
