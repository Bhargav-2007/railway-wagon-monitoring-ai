# 🚂 Railway Wagon Monitoring System with AI

AI-powered railway wagon monitoring system that detects motion blur in real-time using computer vision and provides automated wagon tracking.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![React](https://img.shields.io/badge/React-18.0+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 🌟 Features

- **Real-time Blur Detection** - Detects motion blur using classical CV and deep learning
- **Wagon Detection & Tracking** - Automatic wagon counting and tracking with IoU matching
- **Multi-Camera Support** - IP camera integration (up to 3 cameras simultaneously)
- **Live Streaming Dashboard** - React-based web interface with real-time metrics
- **REST API** - FastAPI backend with comprehensive endpoints
- **High Performance** - 20+ FPS processing on CPU

---

## 🛠️ Tech Stack

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

---

## 📦 Installation

### Prerequisites
```bash
Python 3.8+
Node.js 16+
SQLite / PostgreSQL