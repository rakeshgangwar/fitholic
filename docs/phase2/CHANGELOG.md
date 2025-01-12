# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.3] - 2024-01-12

### Changed
- Enhanced profile management UI components
  - Replaced Flowbite form components with custom styled inputs
  - Improved form field styling with proper focus states and borders
  - Added proper data initialization for form fields
  - Fixed profile data prefilling issues

### Fixed
- Profile data handling in frontend components
  - Corrected API response data extraction
  - Fixed undefined value handling in form fields
  - Improved type safety for profile data
  - Resolved issues with form field default values

## [2.0.2] - 2024-01-12

### Added
- User Profile Management System
  - New API endpoints for profile operations:
    - `GET /profiles/me` for getting current user's profile
    - `POST /profiles/me` for creating user profile
    - `PUT /profiles/me` for updating profile
    - `DELETE /profiles/me` for deleting profile
    - `GET /profiles/{user_id}` for admin access to any profile
  - Profile features include:
    - Personal info (height, weight, date of birth, gender)
    - Fitness goals and preferences
    - App settings (theme, language, units)
    - Notification and privacy settings

- Body Measurements Tracking System
  - New API endpoints for measurements:
    - `GET /measurements/me` for listing measurements
    - `POST /measurements/me` for adding new measurements
    - `GET /measurements/me/{measurement_id}` for specific measurement
    - `PUT /measurements/me/{measurement_id}` for updating measurements
    - `DELETE /measurements/me/{measurement_id}` for deleting measurements
  - Measurement features include:
    - Core measurements (weight, body fat)
    - Detailed body measurements (chest, waist, hips, etc.)
    - Date-based tracking
    - One measurement per day limit

### Changed
- Enhanced user model with profile relationship
- Improved CRUD operations with base class inheritance
- Updated database schema for user profiles and measurements
- Standardized API response formats

### Security
- Added profile ownership validation
- Protected sensitive user data access
- Implemented admin-only routes for user management

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
