# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.15] - 2025-01-21

### Changed
- Enhanced workout status management:
  - Modified workout log status to include "scheduled", "ongoing", and "completed" states
  - Updated database schema to make start_time nullable for scheduled workouts
  - Improved status transitions:
    - Workouts are created as "scheduled" with no start_time
    - Start_time is set when workout status changes to "ongoing"
    - End_time is required for "completed" status
  - Enhanced validation rules for each status state
  - Updated frontend to handle new status workflow

### Fixed
- Fixed workout scheduling to properly handle future workouts
- Fixed start_time handling in workout logs to align with status states
- Fixed validation for workout status transitions

## [2.0.14] - 2025-01-15

### Added
- Added workout session status tracking:
  - New fields in WorkoutLog model: `start_time`, `end_time`, and `status`
  - Migration to handle existing workout logs
  - Enhanced validation for workout completion status
- Added voice command support for workout logging:
  - Speech-to-text for voice input processing
  - Text-to-speech for system responses
  - LangGraph-based command processing system
  - Voice commands for logging sets and navigating exercises

### Changed
- Updated workout logger validation:
  - Modified reps validation to only apply to completed sets
  - Improved exercise completion status handling
  - Enhanced workout completion logic in frontend
- Enhanced voice interaction system:
  - Integrated GPT-4 for natural language understanding
  - Added context-aware command processing
  - Improved error handling in voice processing pipeline

### Fixed
- Fixed JSON serialization in workout log updates
- Fixed exercise skipping functionality
- Fixed complete session button visibility
- Fixed validation issues with ongoing workout sets

## [2.0.13] - 2024-01-15

### Changed
- Updated `WorkoutGenerator` component:
  - Replaced select components with radio buttons for `location` and `intensity` fields.
  - Improved user interface for selecting workout preferences.
- Updated workout-related components to use shadcn components for improved styling and theme awareness:
  - `WorkoutPlanner` component updated with shadcn form elements and layout.
  - `WorkoutLogger` component enhanced with shadcn alerts and progress bars.
  - `WorkoutSummary` component restructured using shadcn cards and alerts.

### Added
- Updated API endpoint `/workouts/generate` to accept new payload structure:
  - Added `WorkoutGenerationParams` model for request validation.
  - Enhanced workout generation logic to use user-provided parameters.
  - Improved error handling and validation for workout generation requests.

## [2.0.12] - 2024-01-14

### Changed
- Updated ExerciseView component to use native HTML buttons with shadcn classes
  - Replaced Button component with HTML button elements
  - Applied shadcn button variants through buttonVariants utility
  - Maintained consistent styling and functionality
  - Improved component performance by reducing component overhead

## [2.0.11] - 2024-01-14

### Changed
- Updated ExerciseView component layout:
  - Moved video section between instructions and exercise headings
  - Placed video on the left side, muscle group and equipment on the right side
  - Improved markdown rendering for instructions
  - Enhanced styling for better visual hierarchy

### Fixed
- Addressed markdown header rendering issues in ExerciseView
- Improved handling of line breaks and markdown syntax in instructions

## [2.0.10] - 2024-01-14

### Changed
- Enhanced UI components with shadcn UI library
  - Updated profile management components:
    - Personal Info form with improved validation
    - App Settings with theme and language controls
    - Notifications panel with better toggles
    - Privacy settings with role-based controls
  - Enhanced exercise management interface:
    - Exercise list with card and table views
    - Exercise form with better organization
    - Exercise filters with improved search
    - Exercise modal with video preview
  - Improved form components:
    - Added proper form validation
    - Enhanced error handling
    - Better loading states
    - Improved accessibility
  - Updated authentication pages:
    - Login page with new design
    - Registration page with matching style
    - Added theme switcher to login page

### Fixed
- Theme synchronization between profile and UI
- Form field validation and error states
- Video URL handling in exercise components
- Message key consistency in translations

## [2.0.9] - 2024-01-13

### Added
- AI-powered Fitness Chatbot implementation
  - New chat-based interface for fitness assistance
  - LangGraph-based conversation workflow management
  - Core components:
    - Message parser for intent identification
    - Exercise creator for personalized exercises
    - Workout generator for quick workout plans
    - Motivation node for general fitness guidance
  - Database models for chat session management:
    - Chat sessions tracking
    - Message history storage
    - Conversation context management
  - API endpoints for chat functionality:
    - Session creation and management
    - Message processing
    - Chat history retrieval

### Changed
- Enhanced AI service architecture with LangGraph integration
- Improved conversation state management
- Updated database schema for chat functionality

### Technical Details
- Implemented stateful conversation handling
- Added robust error handling and recovery
- Enhanced logging for debugging and monitoring
- Improved type safety with Pydantic models

## [2.0.8] - 2024-01-13

### Changed
- Enhanced exercise video player functionality
  - Replaced inline iframes with video thumbnails for better performance
  - Added play button overlay with hover effect
  - Implemented popup video player with autoplay
  - Added click outside to close functionality for video popup
  - Improved keyboard accessibility for video thumbnails
  - Enhanced video player UI with better spacing and transitions
  - Added loading state for video thumbnails

## [2.0.7] - 2024-01-13

### Changed
- Enhanced AI exercise video search functionality
  - Improved YouTube URL parsing to handle different URL formats
  - Added filtering to exclude YouTube Shorts from search results
  - Updated video URL extraction to maintain clean URLs without query parameters
  - Enhanced error handling for video search failures

### Fixed
- YouTube video URL parsing in exercise generation
  - Fixed handling of URL lists returned by YouTube search
  - Corrected URL extraction for regular YouTube videos
  - Resolved issues with query parameter handling
  - Improved error logging for video search failures

## [2.0.6] - 2024-01-13

### Added
- Added internationalization support for exercise management
  - Added translations for all exercise-related strings in English, German, French, Spanish, and Hindi
  - Updated exercise components to use English values for API communication while displaying translated text
  - Added value-label pairs for muscle groups, equipment, difficulty levels, and exercise types
  - Implemented helper functions to convert between API values and translated labels

### Changed
- Updated `ExerciseForm` and `ExerciseList` components to support internationalization
  - Modified form fields to display translated labels while maintaining English values for API calls
  - Updated select options and checkboxes to use value-label pattern
  - Improved type safety by using consistent English values for backend communication

### Fixed
- Fixed language switching functionality in exercise management interface
- Ensured consistent API communication regardless of UI language selection

## [2.0.5] - 2024-01-12

### Changed
- Enhanced AI-powered workout generation system
  - Implemented structured output using LangChain and Pydantic models
  - Added `WorkoutPlan` and `WorkoutExercise` schemas for better type safety
  - Improved prompt template with clearer exercise requirements
  - Enhanced error handling and validation for generated workouts
  - Streamlined workout template creation process

- Improved exercise generation system
  - Migrated to structured output using LangChain
  - Added `ExerciseDetails` Pydantic model for validated output
  - Updated prompt template to use ChatPromptTemplate
  - Enhanced exercise creation workflow with better type safety
  - Improved error handling for exercise generation

### Fixed
- Exercise generation parsing and validation
- Workout template generation reliability
- Type safety in AI-generated content
- Error handling in workout and exercise generation

## [2.0.4] - 2024-01-12

### Added
- AI-powered exercise generation feature
  - New API endpoint `/exercises/generate` for AI-assisted exercise creation
  - Integration with Google's Gemini Pro model for generating exercise details
  - Structured exercise generation with:
    - Exercise type specification
    - Target muscle group targeting
    - Equipment consideration
    - Difficulty level adaptation
    - Special considerations handling
  - Frontend integration with exercise form component
  - Configurable AI settings through environment variables

### Changed
- Enhanced exercise creation workflow with AI assistance
- Updated configuration system to support optional AI features
- Improved error handling for AI-related operations
- Enhanced UUID handling in workout templates and logs
  - Added custom JSON serialization for UUID fields
  - Fixed JSON serialization issues in workout template creation
  - Improved data handling in workout log creation

### Fixed
- UUID serialization in workout templates JSON fields
- Exercise generation error handling and response formatting
- Configuration loading for optional AI features
- Database compatibility issues with UUID fields in JSON columns

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
