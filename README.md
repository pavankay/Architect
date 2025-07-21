# Architect AI Site Planning Tool

An AI-powered site planning and architecture tool that helps users create, visualize, and manage web project architectures with interactive diagrams and real-time collaboration features.

## 🚀 Features

- **AI-Powered Architecture Generation**: Create comprehensive web project architectures using advanced AI
- **Interactive Visualizations**: View and interact with site maps, frontend components, and backend systems
- **Real-time Progress Tracking**: WebSocket-powered progress updates during project generation
- **Dark/Light Theme Support**: Complete theming with proper contrast and accessibility
- **Modern Typography**: Features the elegant Antikor Mono Light font for all titles
- **Responsive Design**: Optimized for desktop and mobile experiences
- **Project Management**: Create, edit, and organize multiple projects with ease

## 🏗️ Architecture

### Frontend
- **Framework**: Astro with TypeScript
- **Styling**: Tailwind CSS with custom design system
- **Components**: Mix of Astro components and React components for interactivity
- **State Management**: React hooks for component state
- **Real-time Updates**: WebSocket integration for live progress tracking

### Backend
- **Framework**: FastAPI (Python)
- **AI Integration**: Advanced language models for architecture generation
- **WebSocket Support**: Real-time communication for progress updates
- **API Design**: RESTful endpoints with comprehensive error handling

## 🛠️ Tech Stack

- **Frontend**: Astro, TypeScript, React, Tailwind CSS
- **Backend**: Python, FastAPI, WebSockets
- **AI**: Large Language Models for architecture generation
- **Development**: Hot reload, TypeScript compilation, Python virtual environments

## 📦 Installation

### Prerequisites
- Node.js (v16 or higher)
- Python (v3.8 or higher)
- npm or yarn

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 5000
```

## 🚀 Development

### Start Development Servers
1. **Frontend** (port 3000):
   ```bash
   cd frontend && npm run dev
   ```

2. **Backend** (port 5000):
   ```bash
   cd backend && uvicorn main:app --reload --port 5000
   ```

3. **Access the application**: http://localhost:3000

### Key Development Commands
- `npm run build` - Build frontend for production
- `npm run preview` - Preview production build
- `python -m pytest` - Run backend tests

## 🎨 Design System

### Typography
- **Titles**: Antikor Mono Light (custom font with uppercase transformation)
- **Body**: System font stack with excellent readability
- **Code**: Monospace fonts for technical content

### Theming
- **Dark Mode**: Deep blacks with accent colors
- **Light Mode**: Clean whites with proper contrast
- **Accessibility**: WCAG compliant color combinations

## 📁 Project Structure

```
site_helper/
├── frontend/           # Astro frontend application
│   ├── src/
│   │   ├── components/ # Reusable UI components
│   │   ├── pages/      # Route pages
│   │   ├── styles/     # Global styles and fonts
│   │   └── fonts/      # Custom font files
├── backend/            # FastAPI backend application
│   ├── main.py        # FastAPI application entry point
│   └── requirements.txt
└── fonts/             # Source font files
```

## 🔧 Key Features Implementation

### Project Creation
- Dedicated create page with enhanced UX
- AI-powered architecture generation
- Real-time progress tracking via WebSockets
- Comprehensive project metadata collection

### Visualization Tools
- **Site Map Viewer**: Interactive hierarchical site structure
- **Frontend Visualizer**: Component architecture and relationships
- **Backend Diagrams**: API structure and data flow visualization

### User Experience
- **Keyboard Shortcuts**: Efficient navigation and actions
- **Responsive Design**: Optimized for all screen sizes
- **Loading States**: Smooth transitions and progress indicators
- **Error Handling**: Graceful error states with recovery options

## 🎯 Recent Updates

- ✅ Implemented Antikor Mono Light font across all titles
- ✅ Fixed light mode visual bugs and theming issues
- ✅ Enhanced create project page with larger description fields
- ✅ Added real-time WebSocket progress tracking
- ✅ Improved sidebar theming and removed grid patterns
- ✅ Added keyboard shortcuts for efficient project management

## 🚀 Deployment

The application is designed for easy deployment with standard web hosting:
- Frontend: Static site generation with Astro
- Backend: ASGI-compatible server deployment
- Environment: Configure API endpoints and AI model access

## 🤝 Contributing

This is a focused development project. Key areas for enhancement:
- Additional visualization types
- Extended AI model integration
- Enhanced collaboration features
- Performance optimizations

## 📄 License

This project is designed for site planning and architecture visualization purposes.

---

Built with ❤️ using modern web technologies and AI-powered architecture generation.