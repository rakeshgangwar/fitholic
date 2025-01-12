# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.1] - 2024-01-12

### Changed
- Project plan updated to move mobile app development from Phase 2 to Phase 4
- Reorganized phase structure to better focus on core web features first

## [2.0.0] - 2024-01-11

### Added
- Exercise management system with comprehensive SQLAlchemy model
  - New API endpoints for CRUD operations:
    - `GET /exercises/` for listing exercises with pagination
    - `POST /exercises/` for creating new exercises
    - `GET /exercises/{exercise_id}` for retrieving specific exercises
    - `PUT /exercises/{exercise_id}` for updating exercises
    - `DELETE /exercises/{exercise_id}` for deleting exercises
    - `POST /exercises/search` for searching exercises by criteria
- Workout template system with User and Exercise model relationships
  - New API endpoints for template management:
    - `GET /workouts/templates/` for listing templates
    - `POST /workouts/templates/` for creating templates
    - `GET /workouts/templates/{template_id}` for retrieving templates
    - `PUT /workouts/templates/{template_id}` for updating templates
    - `DELETE /workouts/templates/{template_id}` for deleting templates
- Workout logging system for tracking completed workouts
  - New API endpoints for workout logging:
    - `GET /workouts/logs/` for listing workout logs
    - `POST /workouts/logs/` for creating workout logs
    - `GET /workouts/logs/{log_id}` for retrieving logs
    - `PUT /workouts/logs/{log_id}` for updating logs
    - `DELETE /workouts/logs/{log_id}` for deleting logs
- Frontend components for workout management:
  - WorkoutPlanner for creating and managing templates
  - WorkoutLogger for tracking workout progress
  - WorkoutSummary for viewing workout history
- Database migrations for new workout-related tables
- Type definitions for all workout-related components

### Changed
- Enhanced User model with workout templates and logs relationships
- Updated database schema to support workout management
- Improved API error handling and input validation
- Refactored frontend routing and navigation structure
- Integrated workout components into main dashboard layout
- Enhanced API documentation with detailed response schemas

### Fixed
- API endpoint prefixes and routing configuration
- Authentication token handling in API requests
- Workout template validation and error responses
- Python cache directory handling in Alembic versions
- Required files and directories management in .gitignore

### Security
- Improved authentication token validation
- Enhanced user permission checks for workout operations

[2.0.0]: https://github.com/username/fitholic/releases/tag/v2.0.0
