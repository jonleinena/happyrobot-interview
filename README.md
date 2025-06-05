# HappyRobot Carrier Engagement API - Solutions Engineer Interview

This is Jon Leiñena's implementation of the Happyrobot Solutions Engineer Interview technical take home assignment.

The current proposed solution is a comprehensive FastAPI-based app for AI-powered inbound carrier engagement and load matching, with dashboard visualization.

## Overview

This API implements a real-world use case for inbound carrier engagement where AI assistants can receive calls from carriers looking to book loads. The system handles carrier verification through FMCSA API, load searching and matching, rate negotiations, and comprehensive call outcome tracking.

## Architecture

### Core Components

- **FastAPI Backend**: High-performance API framework with automatic OpenAPI documentation
- **PostgreSQL Database**: Robust data storage for loads, carriers, and call logs
- **FMCSA Integration**: Real-time carrier verification using Department of Transportation API
- **Docker Containerization**: Consistent deployment across environments
- **Google Cloud Run**: Serverless deployment with automatic HTTPS and scaling

### API Endpoints

- **Health Checks**: `/health` and `/health/db` for system monitoring
- **Carrier Verification**: `/api/v1/carriers/verify/{mc_number}` for FMCSA validation
- **Load Management**: `/api/v1/loads/{load_id}` for load searching and filtering
- **Call Logging**: `/api/v1/offers/log` for recording call outcomes
- **Dashboard**: `/api/v1/offers/dashboard` for call metrics and reporting

### Security Features

- API key authentication for all endpoints
- Environment-based configuration management
- CORS middleware for cross-origin requests
- Trusted host middleware for production security
- Secret management through Google Cloud Secret Manager

## Key Features Implemented

### 1. Carrier Verification
- Real-time MC number validation through FMCSA API
- Carrier status verification (ACTIVE, SUSPENDED, INACTIVE)
- DOT number cross-referencing
- Carrier name and details retrieval

### 2. Load Matching System
- Advanced filtering by origin, destination, equipment type
- Date-based pickup scheduling
- Weight and rate range filtering
- Multi-criteria search capabilities
- Pagination and result limiting

### 3. Reporting Dashboard
The system includes a built-in HTML dashboard accessible at `/api/v1/offers/dashboard?api_key=your_key`. This dashboard was implemented directly within the API rather than as a separate React application to prioritize development speed and simplicity. While this approach may not be as sophisticated as a dedicated frontend framework, it follows the principle of "good > perfect" and allowed for rapid implementation without extending the development timeline unnecessarily.

The dashboard provides:
- Real-time call metrics and statistics
- Booking rate calculations
- Average negotiation rounds tracking
- Detailed call log tables with filtering
- Sentiment analysis visualization
- FMCSA verification status tracking

## Local Development

### Prerequisites
- Docker and Docker Compose
- Git

### Quick Start

1. Clone the repository:
```bash
git clone https://github.com/jonleinena/happyrobot-interview.git
cd happyrobot-interview
```

2. Start the application with Docker Compose:
```bash
docker compose up --build -d
```

3. Verify the API is running:
```bash
curl http://localhost:8000/health
```

The API will be available at `http://localhost:8000` with the following default configuration:
- PostgreSQL database on port 5432
- API server on port 8000
- Automatic database initialization
- Development environment with hot reload

### Environment Variables

Create a `.env` file with the following variables:
```bash
API_KEY=your-api-key-for-happyrobot-integration
FMCSA_API_KEY=your-fmcsa-api-key
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/myapp
ENVIRONMENT=development
```

## Production Deployment

### Google Cloud Run

The application is deployed on Google Cloud Run, which automatically provides:
- HTTPS encryption with managed SSL certificates
- Custom domain support (if configured)
- Automatic scaling based on traffic
- Global CDN and load balancing
- Integration with Google Cloud services

**Live Deployment**: https://happyrobot-api-1032128188704.us-central1.run.app/

You can test the deployment with a health check:
```bash
curl https://happyrobot-api-1032128188704.us-central1.run.app/health
```

### Deployment Reproduction

For detailed instructions on reproducing the deployment, including:
- Google Cloud project setup
- Cloud SQL database configuration
- Secret Manager setup
- Container registry and deployment
- Post-deployment database initialization

Refer to the comprehensive guide in `DEPLOYMENT.MD`.

### Containerization

The application is fully containerized using Docker:

**Dockerfile Features**:
- Multi-stage build optimization
- Non-root user security
- Minimal Python 3.11 slim base image
- Optimized layer caching
- Environment-specific configuration

**Docker Compose Features**:
- PostgreSQL database with health checks
- Development volume mounting for hot reload
- Environment variable configuration
- Service dependency management
- Persistent data storage

## API Authentication

All endpoints require API key authentication via the `Authorization: ApiKey your-key` header:

```bash
curl -H "Authorization: ApiKey your-api-key" https://happyrobot-api-1032128188704.us-central1.run.app/api/v1/loads/
```

## Database Schema

### Loads Table
- Complete load information including origin, destination, rates
- Equipment type and commodity classification
- Pickup and delivery scheduling
- Weight, dimensions, and piece count tracking

### Call Logs Table
- HappyRobot run ID correlation
- MC number and carrier verification status
- Negotiation tracking and rate agreements
- Call outcome and sentiment classification
- Raw extracted data storage for analysis

## Integration with HappyRobot Platform

The API is designed to integrate seamlessly with the HappyRobot platform for:
- Inbound call handling and AI assistant interaction
- Real-time carrier verification during calls
- Dynamic load searching based on carrier requirements
- Automated call outcome logging and classification
- Dashboard reporting for campaign performance

## Development Decisions

### Speed vs Perfection
This implementation prioritizes rapid development and functional completeness over architectural perfection. Key decisions include:

- **Integrated Dashboard**: Built directly into the API rather than a separate React application to accelerate development
- **FastAPI Choice**: Leverages automatic documentation and type validation for faster iteration
- **Docker Containerization**: Ensures consistent deployment across environments without complex setup
- **Google Cloud Run**: Provides production-ready deployment with minimal configuration overhead

### Technical Trade-offs
- Dashboard is HTML-based rather than a sophisticated front-end framework
- Simplified authentication using API keys rather than OAuth/JWT
- Embedded reporting rather than separate analytics service

These decisions have been made to speed up the implementation with the goal to not extend the interview process unnecessarily.

## Future Enhancements

Potential improvements for production use:
- Advanced analytics and reporting capabilities
- Real-time WebSocket connections for live updates
- Enhanced authentication and authorization
- Comprehensive logging and monitoring
- API rate limiting and throttling
- Advanced caching strategies
- Microservices architecture for scale
- Dedicated front-end

