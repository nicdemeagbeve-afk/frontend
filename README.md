# Frontend Documentation

## Overview

This project is a web application that serves as the frontend for the Box-AI WhatsApp Bot with AI integration. It interacts with the backend API to provide a user interface for authentication and dashboard functionalities.

## Project Structure

The frontend is structured as follows:

```
frontend
├── package.json          # Configuration file for npm, listing dependencies and scripts
├── public                # Contains static files served to the client
│   ├── index.html        # Main HTML file for the application
│   ├── dashboard.html     # HTML file for the dashboard view
│   ├── css               # Directory for CSS files
│   │   └── style.css     # Styles for the frontend
│   └── js                # Directory for JavaScript files
│       ├── auth.js       # JavaScript file for authentication logic
│       └── dashboard.js   # JavaScript file for dashboard functionality
```

## Installation

To get started with the frontend, follow these steps:

1. Clone the repository:
   ```
   git clone <repository-url>
   cd box-ai/frontend
   ```

2. Install the dependencies:
   ```
   npm install
   ```

## Running the Frontend

To run the frontend application in development mode, use the following command:

```
npm start
```

This will start a local server and you can access the application at `http://localhost:3000`.

## Deployment

You can deploy the frontend separately on a static site hosting service like Vercel or Netlify. Follow the respective service's documentation for deployment instructions.

## Features

- User authentication
- Dashboard for managing interactions with the WhatsApp Bot
- Responsive design for various devices

## Contributing

If you would like to contribute to this project, please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the ISC License.