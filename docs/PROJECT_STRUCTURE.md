# Project Structure

## Overview

GPT PANELIN V3.2 is a modern React-based web application for interacting with GPT models. This document provides an overview of the repository structure.

## Directory Structure

```
GPT-PANELIN-V3.2/
├── .github/              # GitHub Actions workflows and configurations
│   └── workflows/
│       └── ci-cd.yml    # CI/CD pipeline configuration
├── docs/                # Documentation files
│   ├── API.md          # API documentation
│   └── DEPLOYMENT.md   # Deployment guide
├── public/             # Static assets
│   └── favicon.svg     # Application favicon
├── src/                # Source code
│   ├── components/     # React components
│   │   ├── ChatPanel.jsx    # Main chat interface component
│   │   └── Header.jsx       # Header component
│   ├── config/         # Configuration files
│   │   └── config.js   # Application configuration
│   ├── styles/         # CSS stylesheets
│   │   ├── App.css          # Main app styles
│   │   ├── ChatPanel.css    # Chat panel styles
│   │   ├── Header.css       # Header styles
│   │   └── index.css        # Global styles
│   ├── utils/          # Utility functions
│   │   └── api.js      # API client utilities
│   ├── App.jsx         # Main application component
│   └── index.jsx       # Application entry point
├── .env.example        # Environment variables template
├── .eslintrc.json      # ESLint configuration
├── .gitignore          # Git ignore rules
├── .prettierrc.json    # Prettier configuration
├── CHANGELOG.md        # Version history
├── CONTRIBUTING.md     # Contributing guidelines
├── Dockerfile          # Docker container configuration
├── LICENSE             # MIT License
├── README.md           # Project readme
├── SECURITY.md         # Security policy
├── docker-compose.yml  # Docker Compose configuration
├── index.html          # HTML entry point
├── nginx.conf          # Nginx configuration for production
├── package.json        # Node.js dependencies and scripts
└── vite.config.js      # Vite build tool configuration
```

## Key Files

### Configuration Files

- **package.json**: Defines project dependencies, scripts, and metadata
- **vite.config.js**: Vite bundler configuration for development and production builds
- **.eslintrc.json**: Code linting rules and standards
- **.prettierrc.json**: Code formatting rules
- **.env.example**: Template for environment variables

### Application Files

- **index.html**: Main HTML template
- **src/index.jsx**: Application entry point that mounts React to the DOM
- **src/App.jsx**: Main application component that orchestrates the UI
- **src/components/**: Reusable React components

### Docker Files

- **Dockerfile**: Multi-stage Docker build for production
- **docker-compose.yml**: Docker Compose configuration for easy deployment
- **nginx.conf**: Nginx web server configuration

### Documentation

- **README.md**: Quick start and overview
- **docs/DEPLOYMENT.md**: Detailed deployment instructions
- **docs/API.md**: API integration documentation
- **CONTRIBUTING.md**: Guidelines for contributors
- **SECURITY.md**: Security policy and best practices
- **CHANGELOG.md**: Version history and changes

## Technology Stack

### Frontend
- **React 18**: UI framework
- **Vite**: Build tool and development server
- **Axios**: HTTP client for API requests

### Development Tools
- **ESLint**: Code linting
- **Prettier**: Code formatting
- **Vite**: Fast build tool with HMR

### Deployment
- **Docker**: Containerization
- **Nginx**: Production web server
- **GitHub Actions**: CI/CD automation

## Build Output

When you run `npm run build`, Vite generates optimized production files in the `dist/` directory:

```
dist/
├── assets/          # Bundled and minified JS/CSS
├── favicon.svg      # Application icon
└── index.html       # Production HTML
```

## Development Workflow

1. **Clone** the repository
2. **Install** dependencies with `npm install`
3. **Configure** environment variables in `.env`
4. **Develop** with `npm run dev` (starts dev server)
5. **Lint** code with `npm run lint`
6. **Format** code with `npm run format`
7. **Build** for production with `npm run build`
8. **Preview** production build with `npm run preview`

## Scripts

- `npm run dev`: Start development server with hot reload
- `npm run build`: Create production build
- `npm run preview`: Preview production build locally
- `npm run lint`: Run ESLint to check code quality
- `npm run lint:fix`: Auto-fix linting issues
- `npm run format`: Format code with Prettier

## Environment Variables

See `.env.example` for all available configuration options. Key variables:

- `VITE_API_BASE_URL`: Backend API endpoint
- `VITE_OPENAI_API_KEY`: OpenAI API key (for direct integration)
- `VITE_OPENAI_MODEL`: GPT model to use

## Getting Help

- Check the [README.md](../README.md) for quick start guide
- Read [DEPLOYMENT.md](docs/DEPLOYMENT.md) for deployment options
- See [API.md](docs/API.md) for API integration details
- Review [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines
- Check [SECURITY.md](../SECURITY.md) for security best practices
