# Fitholic

Fitholic is an AI-powered fitness and wellness platform that helps users create personalized workout routines, track progress, and receive guidance on their fitness journey.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running Locally](#running-locally)
- [AI Agents](#ai-agents)
  - [Agent Types](#agent-types)
  - [Agent Workflows](#agent-workflows)
- [Development Phases](#development-phases)
- [Contributing](#contributing)
- [License](#license)

## Overview

Fitholic is designed to provide a comprehensive fitness experience by leveraging AI to create personalized workout plans, analyze exercise form, generate nutrition guidance, and keep users motivated throughout their fitness journey.

The application combines modern web technologies with AI capabilities to deliver a seamless and intelligent fitness companion that adapts to each user's unique needs and goals.

## Features

- **Personalized Workout Generation**: AI-generated workout plans based on user goals, fitness level, and available equipment
- **Exercise Library**: Comprehensive database of exercises with detailed instructions and video demonstrations
- **Workout Tracking**: Log and track workout progress over time
- **User Profiles**: Customizable user profiles with fitness goals, preferences, and measurements
- **AI Chat Interface**: Intelligent chatbot for workout advice, exercise creation, and motivation
- **Form Analysis**: AI-powered exercise form analysis and feedback (coming soon)
- **Nutrition Planning**: Personalized nutrition guidance and meal planning (coming soon)

## Tech Stack

### Frontend
- **Framework**: SvelteKit
- **Styling**: TailwindCSS
- **State Management**: Svelte stores
- **Testing**: Playwright, Vitest

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL (via Supabase)
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Testing**: Pytest

### AI & Machine Learning
- **LLM Framework**: LangChain
- **Workflow Orchestration**: LangGraph
- **Models**: GPT-4o, Gemini Pro

## Project Structure

```
fitholic/
├── apps/
│   ├── api/             # FastAPI backend
│   │   ├── app/         # API application
│   │   │   ├── agents/  # AI agents and workflows
│   │   │   ├── api/     # API endpoints
│   │   │   ├── core/    # Core functionality
│   │   │   ├── db/      # Database models and queries
│   │   │   ├── schemas/ # Pydantic schemas
│   │   │   └── services/# Business logic services
│   │   ├── tests/       # Backend tests
│   │   └── alembic/     # Database migrations
│   └── web/             # SvelteKit frontend
│       ├── src/         # Frontend source code
│       │   ├── lib/     # Components and utilities
│       │   └── routes/  # Application routes
│       └── static/      # Static assets
└── docs/                # Project documentation
    ├── main/           # Main project documentation
    ├── phase1/         # Phase 1 documentation
    ├── phase2/         # Phase 2 documentation
    ├── phase3/         # Phase 3 documentation
    └── phase4/         # Phase 4 documentation
```

## Getting Started

### Prerequisites

- Node.js (v18+)
- Python (v3.10+)
- PostgreSQL or Supabase account
- LLM API keys (OpenAI and/or Google Gemini)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fitholic.git
cd fitholic
```

2. Install API dependencies:
```bash
cd apps/api
python -m pip install poetry
poetry install
```

3. Install web dependencies:
```bash
cd ../web
npm install
```

4. Set up environment variables:
- Create `.env` files in both `apps/api` and `apps/web` directories based on the provided templates

### Running Locally

1. Start the API server:
```bash
cd apps/api
poetry run python run.py
```

2. Start the web development server:
```bash
cd apps/web
npm run dev
```

3. Open your browser and navigate to `http://localhost:5173`

## AI Agents

Fitholic uses a multi-agent AI system to provide personalized fitness guidance. The agents are built using LangChain and orchestrated with LangGraph.

### Agent Types

1. **Workout Generator Agent**
   - **Purpose**: Creates personalized workout plans based on user profiles and preferences
   - **Configuration**: Uses GPT-4o with temperature of 0.7
   - **System Prompt**: Expert fitness trainer specialized in creating personalized workout plans

2. **Form Analysis Agent**
   - **Purpose**: Analyzes exercise form and provides feedback for improvement
   - **Configuration**: Uses GPT-4o with temperature of 0.7
   - **System Prompt**: Expert in exercise form and biomechanics

3. **Motivation Agent**
   - **Purpose**: Provides encouragement and motivation to keep users consistent
   - **Configuration**: Uses GPT-4o with temperature of 0.7
   - **System Prompt**: Encouraging fitness coach focused on keeping users motivated

4. **Chat System Agents**
   - **Message Parser Node**: Analyzes user chat messages to determine intent
   - **Exercise Creator Node**: Creates custom exercises based on user requirements
   - **Workout Generator Node**: Generates workout plans via chat interface
   - **Router Node**: Routes conversation flow based on detected intent

### Agent Workflows

1. **Dynamic Workout Generation Workflow**
   - **Components**: User profile input → Workout generation → Feedback collection → Workout adjustment
   - **Implementation**: Uses LangGraph to orchestrate the flow between nodes
   - **Sample Flow**: User provides fitness goals → Agent generates workout → User provides feedback → Agent refines workout

2. **Fitness Chat Workflow**
   - **Components**: Message parsing → Intent routing → Specialized nodes (exercise creation, workout generation, motivation)
   - **Implementation**: Uses a conditional edge graph to dynamically route conversations
   - **Sample Flow**: User asks about an exercise → Parser identifies intent → Router routes to appropriate node → Response generated

3. **Future Workflows** (In Development)
   - **Nutrition Planning**: Will include dietary needs analysis and meal plan generation
   - **Form Analysis**: Will include video input processing and pose estimation
   - **Educational Content Delivery**: Will provide personalized fitness education

## Development Phases

The project is being developed in multiple phases:

1. **Phase 1: Foundation** (Weeks 1-4)
   - Core infrastructure setup
   - Backend development
   - Database implementation
   - Basic frontend

2. **Phase 2: Core Features** (Weeks 5-8)
   - Workout management
   - User profiles
   - Basic AI integration
   - Security enhancements

3. **Phase 3: Advanced Features** (Weeks 9-12)
   - AI-powered form analysis
   - Nutrition planning
   - Social features
   - Performance optimization

4. **Phase 4: Refinement and Launch** (Weeks 13-16)
   - Final polishing
   - Comprehensive testing
   - Documentation
   - Deployment and launch

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 