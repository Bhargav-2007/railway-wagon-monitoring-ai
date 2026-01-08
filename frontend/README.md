# Railway Wagon Monitoring System with AI

AI-powered railway wagon monitoring system that detects motion blur in real-time using computer vision and provides automated wagon tracking.

![Python](https://img.shields.io/badge/Python-3.8+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green) ![React](https://img.shields.io/badge/React-18.0+-blue) ![License](https://img.shields.io/badge/License-MIT-yellow)

## Features

- **Real-time Blur Detection** - Detects motion blur using classical CV and deep learning
- **Wagon Detection & Tracking** - Automatic wagon counting and tracking with IoU matching
- **Multi-Camera Support** - IP camera integration (up to 3 cameras simultaneously)
- **Live Streaming Dashboard** - React-based web interface with real-time metrics
- **REST API** - FastAPI backend with comprehensive endpoints
- **High Performance** - 20+ FPS processing on CPU

## Tech Stack

### Backend
- **FastAPI** - High-performance async Python web framework
- **OpenCV** - Computer vision and image processing
- **SQLAlchemy** - Database ORM
- **NumPy** - Numerical computations

### Frontend
- **React 18** - Modern UI framework
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Recharts** - Data visualization
- **Redux Toolkit** - State management

### AI Pipeline
- **Custom Blur Detection** - Laplacian variance & FFT analysis
- **Classical CV Algorithms** - Contour-based wagon detection
- **Real-time Tracking** - IoU-based wagon tracking
- **20+ FPS** - Optimized for CPU performance

## Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- SQLite / PostgreSQL

### Frontend Setup

```bash
cd frontend
npm install
```

### Backend Setup

```bash
pip install -r requirements.txt
```

## Running the Application

### Start Frontend (React Development Server)

```bash
cd frontend
npm start
```

The frontend will be available at `http://localhost:3000`

### Start Backend (FastAPI Server)

```bash
cd backend
python main.py
```

The API will be available at `http://localhost:8000`

## Frontend Dependencies

### Main Dependencies
- **react** - ^19.2.3 - Core React library
- **react-dom** - ^19.2.3 - React DOM rendering
- **react-router-dom** - ^6.20.0 - Client-side routing
- **react-scripts** - 5.0.1 - Create React App build scripts
- **typescript** - ^4.9.5 - TypeScript compiler

### UI & Styling
- **tailwindcss** - Utility-first CSS framework
- **@emotion/react** - ^11.14.0 - CSS-in-JS solution
- **@emotion/styled** - ^11.14.0 - Styled components with Emotion
- **clsx** - ^2.1.1 - Conditional classname utility
- **lucide-react** - ^0.562.0 - Icon library

### Data & Visualization
- **recharts** - ^3.6.0 - Composable charting library
- **axios** - ^1.6.2 - HTTP client
- **date-fns** - ^2.30.0 - Modern date utility library

### Real-time Communication
- **socket.io-client** - ^4.6.0 - WebSocket client for real-time updates

### Type Definitions
- **@types/react** - ^19.2.7
- **@types/react-dom** - ^19.2.3
- **@types/react-router-dom** - ^5.3.3
- **@types/jest** - ^27.5.2
- **@types/node** - ^16.18.126

### Testing
- **@testing-library/react** - ^16.3.1
- **@testing-library/jest-dom** - ^6.9.1
- **@testing-library/dom** - ^10.4.1
- **@testing-library/user-event** - ^13.5.0

### Build & Performance
- **web-vitals** - ^2.1.4 - Web performance metrics

## Available Scripts

### npm start
Runs the app in development mode. Open [http://localhost:3000](http://localhost:3000) to view it in your browser. The page will reload when you make changes.

### npm test
Launches the test runner in interactive watch mode.

### npm run build
Builds the app for production to the `build` folder.

### npm run eject
**Note: this is a one-way operation. Once you eject, you can't go back!**

If you aren't satisfied with the build tool and configuration choices, you can eject at any time. This command will remove the single build dependency from your project.

## Configuration

### Tailwind CSS
Tailwind configuration is in `tailwind.config.js`

### PostCSS
PostCSS configuration is in `postcss.config.js`

### TypeScript
TypeScript configuration is in `tsconfig.json`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.