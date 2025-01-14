## Database Schema Documentation (v1)

This document outlines the current database schema and future plans for the Fitholic application.

### Implemented Tables

**1. Users**

| Column | Data Type | Constraints | Description |
|---|---|---|---|
| user_id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique identifier for each user |
| email | TEXT | UNIQUE, NOT NULL | User's email address |
| password | TEXT | NOT NULL | Hashed password using bcrypt |
| first_name | TEXT |  | User's first name |
| last_name | TEXT |  | User's last name |
| date_of_birth | DATE |  | User's date of birth |
| gender | TEXT |  | User's gender |
| height | NUMERIC(3,2) |  | User's height in meters |
| weight | NUMERIC(5,2) |  | User's weight in kilograms |
| activity_level | TEXT |  | User's activity level |
| fitness_goals | TEXT[] |  | Array of user's fitness goals |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT now() | Timestamp of user creation |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT now() | Timestamp of last user update |

**2. Exercises**

| Column | Data Type | Constraints | Description |
|---|---|---|---|
| exercise_id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique identifier for each exercise |
| name | TEXT | NOT NULL | Name of the exercise |
| description | TEXT |  | Description of the exercise |
| muscle_group | TEXT[] |  | Array of muscle groups targeted |
| equipment | TEXT[] |  | Array of required equipment |
| difficulty | TEXT |  | Difficulty level |
| instructions | TEXT |  | Exercise instructions |
| video_url | TEXT |  | YouTube video URL |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT now() | Creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT now() | Last update timestamp |

**3. Workout Templates**

| Column | Data Type | Constraints | Description |
|---|---|---|---|
| template_id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique identifier |
| user_id | UUID | NOT NULL, FOREIGN KEY (Users) | Template owner |
| name | TEXT | NOT NULL | Template name |
| description | TEXT |  | Template description |
| exercises | JSONB | NOT NULL | Exercise configuration |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT now() | Creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT now() | Last update timestamp |

**4. Workout Logs**

| Column | Data Type | Constraints | Description |
|---|---|---|---|
| log_id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique identifier |
| user_id | UUID | NOT NULL, FOREIGN KEY (Users) | Log owner |
| template_id | UUID | FOREIGN KEY (WorkoutTemplates) | Associated template |
| start_time | TIMESTAMP WITH TIME ZONE | NOT NULL | Workout start time |
| end_time | TIMESTAMP WITH TIME ZONE |  | Workout end time |
| exercises_performed | JSONB | NOT NULL | Exercise performance data |
| notes | TEXT |  | Workout notes |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT now() | Creation timestamp |

**5. Body Measurements**

| Column | Data Type | Constraints | Description |
|---|---|---|---|
| measurement_id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique identifier |
| user_id | UUID | NOT NULL, FOREIGN KEY (Users) | Measurement owner |
| date | DATE | NOT NULL | Measurement date |
| weight | NUMERIC(5,2) |  | Weight in kg |
| body_fat | NUMERIC(4,1) |  | Body fat percentage |
| chest | NUMERIC(4,1) |  | Chest measurement in cm |
| waist | NUMERIC(4,1) |  | Waist measurement in cm |
| hips | NUMERIC(4,1) |  | Hips measurement in cm |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT now() | Creation timestamp |

### Planned Tables (Phase 3)

**6. Nutrition Logs**

| Column | Data Type | Constraints | Description |
|---|---|---|---|
| log_id | UUID | PRIMARY KEY | Unique identifier |
| user_id | UUID | NOT NULL, FOREIGN KEY | Log owner |
| date | DATE | NOT NULL | Log date |
| meals | JSONB | NOT NULL | Meal entries |
| total_calories | INTEGER |  | Total daily calories |
| total_protein | INTEGER |  | Total daily protein |
| total_carbs | INTEGER |  | Total daily carbs |
| total_fat | INTEGER |  | Total daily fat |
| notes | TEXT |  | Daily notes |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT now() | Creation timestamp |

**7. Goals**

| Column | Data Type | Constraints | Description |
|---|---|---|---|
| goal_id | UUID | PRIMARY KEY | Unique identifier |
| user_id | UUID | NOT NULL, FOREIGN KEY | Goal owner |
| type | TEXT | NOT NULL | Goal type |
| target | JSONB | NOT NULL | Target metrics |
| start_date | DATE | NOT NULL | Start date |
| end_date | DATE |  | Target end date |
| status | TEXT | NOT NULL | Goal status |
| progress | JSONB |  | Progress data |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT now() | Creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT now() | Last update |

**8. Social Features (Phase 3)**

| Column | Data Type | Constraints | Description |
|---|---|---|---|
| social_id | UUID | PRIMARY KEY | Unique identifier |
| user_id | UUID | NOT NULL, FOREIGN KEY | Content owner |
| type | TEXT | NOT NULL | Content type |
| content | JSONB | NOT NULL | Social content |
| visibility | TEXT | NOT NULL | Content visibility |
| likes | INTEGER | DEFAULT 0 | Like count |
| comments | JSONB |  | Comment data |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT now() | Creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT now() | Last update |

### Database Optimizations

1. **Indexes**
   - User lookup by email
   - Exercise search by name and muscle groups
   - Workout log queries by date range
   - Measurement queries by date range

2. **Partitioning**
   - Workout logs by date
   - Measurements by date
   - Nutrition logs by date (planned)

3. **Performance**
   - Materialized views for analytics
   - Regular VACUUM and maintenance
   - Query optimization
   - Proper indexing strategy

### Security Measures

1. **Data Protection**
   - Encrypted sensitive data
   - Row-level security
   - Regular backups
   - Audit logging

2. **Access Control**
   - Role-based access
   - Connection pooling
   - Statement timeouts
   - Resource limits

This schema documentation reflects the current state of the database and outlines planned additions for future phases. Regular reviews and updates will be performed as the application evolves. 