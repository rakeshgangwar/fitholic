# Changelog
All notable changes to the Fitholic project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2024-01-11

### Added
- Initial project setup
  - Created monorepo structure with directories for mobile, API, and AI services
  - Set up Poetry for dependency management
  - Configured Git flow for version control
  - Added development dependencies (pytest, black, flake8, etc.)

- Backend Infrastructure
  - Implemented FastAPI application structure
  - Set up configuration management with pydantic-settings
  - Added CORS middleware
  - Created health check endpoint

- Database Setup
  - Configured PostgreSQL database connection
  - Set up SQLAlchemy ORM
  - Implemented Alembic for database migrations
  - Created initial users table migration

- Authentication System
  - Implemented user registration endpoint
  - Added login endpoint with JWT token generation
  - Created password hashing utilities using bcrypt
  - Set up JWT token validation middleware
  - Added user authentication dependencies

### Dependencies
- Core Dependencies
  - FastAPI v0.115.6
  - SQLAlchemy v2.0.37
  - Pydantic v2.10.5
  - Uvicorn v0.34.0

- Authentication
  - python-jose v3.3.0
  - passlib v1.7.4
  - bcrypt v4.1.2
  - python-multipart v0.0.9

- Database
  - psycopg2-binary v2.9.9
  - alembic v1.13.1

- Development Tools
  - pytest v7.4.4
  - black v23.12.1
  - flake8 v7.0.0
  - isort v5.13.2

### Security
- Implemented secure password hashing
- Added JWT-based authentication
- Configured CORS policies
- Set up environment-based configuration

### Technical Debt
- Need to update CORS settings for production
- Add comprehensive test coverage
- Implement request rate limiting
- Add API documentation 

## [0.1.1] - 2024-01-12

### Changed
- Removed rate limiting functionality to be implemented in Phase 2
- Updated API documentation in FastAPI app description
- Improved CORS configuration with environment-specific settings

### Added
- Comprehensive test suite
  - User registration tests
  - Authentication tests
  - Health check endpoint tests
  - Database cleanup between tests
  - Test fixtures for FastAPI app and async client

### Fixed
- Fixed user registration response format
- Improved error handling in authentication endpoints
- Updated configuration to use proper database URL format

### Technical Debt
- Implement rate limiting in Phase 2
- Address deprecation warnings:
  - Update datetime.utcnow() to use timezone-aware objects
  - Migrate to Pydantic v2 ConfigDict
  - Update pytest-asyncio event loop fixture
- Improve test coverage for API dependencies (currently at 83%) 