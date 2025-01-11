**1. Users**

| Column | Data Type | Constraints | Description |
|---|---|---|---|
| user_id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique identifier for each user |
| email | TEXT | UNIQUE, NOT NULL | User's email address |
| password | TEXT | NOT NULL | Hashed password (use Supabase Auth for secure storage) |
| first_name | TEXT |  | User's first name |
| last_name | TEXT |  | User's last name |
| date_of_birth | DATE |  | User's date of birth |
| gender | TEXT |  | User's gender |
| height | NUMERIC(3,2) |  | User's height in meters |
| weight | NUMERIC(5,2) |  | User's weight in kilograms |
| activity_level | TEXT |  | User's activity level (e.g., sedentary, lightly active, active) |
| fitness_goals | TEXT[] |  | Array of user's fitness goals (e.g., weight loss, muscle gain, improve endurance) |
| dietary_preferences | JSONB |  | Flexible JSONB field to store dietary preferences (e.g., vegetarian, vegan, allergies) |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT now() | Timestamp of user creation |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT now() | Timestamp of last user update |

**2. Workouts**

| Column | Data Type | Constraints | Description |
|---|---|---|---|
| workout_id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique identifier for each workout |
| user_id | UUID | NOT NULL, FOREIGN KEY (Users) | ID of the user who performed the workout |
| workout_date | DATE | NOT NULL | Date of the workout |
| start_time | TIMESTAMP WITH TIME ZONE |  | Timestamp of workout start |
| end_time | TIMESTAMP WITH TIME ZONE |  | Timestamp of workout end |
| workout_type | TEXT |  | Type of workout (e.g., strength training, cardio, yoga) |
| total_calories_burned | NUMERIC(5,2) |  | Estimated calories burned during the workout |
| notes | TEXT |  | User's notes about the workout |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT now() | Timestamp of workout creation |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT now() | Timestamp of last workout update |

**3. Exercises**

| Column | Data Type | Constraints | Description |
|---|---|---|---|
| exercise_id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique identifier for each exercise |
| name | TEXT | NOT NULL | Name of the exercise |
| description | TEXT |  | Description of the exercise |
| muscle_group | TEXT[] |  | Array of muscle groups targeted by the exercise |
| equipment | TEXT[] |  | Array of equipment required for the exercise |
| difficulty | TEXT |  | Difficulty level of the exercise (e.g., beginner, intermediate, advanced) |
| instructions | TEXT |  | Step-by-step instructions for performing the exercise |
| video_url | TEXT |  | URL of a video demonstrating the exercise |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT now() | Timestamp of exercise creation |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT now() | Timestamp of last exercise update |

**4. WorkoutExercises (Junction Table)**

| Column | Data Type | Constraints | Description |
|---|---|---|---|
| workout_exercise_id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique identifier for each workout-exercise combination |
| workout_id | UUID | NOT NULL, FOREIGN KEY (Workouts) | ID of the workout |
| exercise_id | UUID | NOT NULL, FOREIGN KEY (Exercises) | ID of the exercise |
| sets | INTEGER |  | Number of sets performed |
| reps | INTEGER |  | Number of repetitions performed per set |
| weight | NUMERIC(5,2) |  | Weight used for the exercise (if applicable) |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT now() | Timestamp of record creation |

**5.  Nutrition**

| Column | Data Type | Constraints | Description |
|---|---|---|---|
| nutrition_log_id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique identifier for each nutrition log entry |
| user_id | UUID | NOT NULL, FOREIGN KEY (Users) | ID of the user who logged the food |
| food_name | TEXT | NOT NULL | Name of the food item |
| calories | NUMERIC(5,2) |  | Calories in the food item |
| protein | NUMERIC(5,2) |  | Protein content in grams |
| carbohydrates | NUMERIC(5,2) |  | Carbohydrate content in grams |
| fat | NUMERIC(5,2) |  | Fat content in grams |
| logged_at | TIMESTAMP WITH TIME ZONE | DEFAULT now() | Timestamp of the food log entry |

**6.  MealPlans**

| Column | Data Type | Constraints | Description |
|---|---|---|---|
| meal_plan_id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique identifier for each meal plan |
| user_id | UUID | NOT NULL, FOREIGN KEY (Users) | ID of the user the meal plan is for |
| meal_date | DATE | NOT NULL | Date of the meal plan |
| meals | JSONB |  | JSONB to store meal details (breakfast, lunch, dinner, snacks) with recipe IDs |
| total_calories | NUMERIC(5,2) |  | Total calories for the meal plan |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT now() | Timestamp of meal plan creation |

**7.  Recipes**

| Column | Data Type | Constraints | Description |
|---|---|---|---|
| recipe_id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique identifier for each recipe |
| name | TEXT | NOT NULL | Name of the recipe |
| ingredients | TEXT[] |  | Array of ingredients |
| instructions | TEXT |  | Recipe instructions |
| image_url | TEXT |  | URL of the recipe image |
| calories | NUMERIC(5,2) |  | Calories per serving |
| protein | NUMERIC(5,2) |  | Protein content per serving |
| carbohydrates | NUMERIC(5,2) |  | Carbohydrate content per serving |
| fat | NUMERIC(5,2) |  | Fat content per serving |
| source | TEXT |  | Source of the recipe (e.g., API, user-submitted) |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT now() | Timestamp of recipe creation |

**8. Content**

| Column | Data Type | Constraints | Description |
|---|---|---|---|
| content_id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique identifier for each content item |
| title | TEXT | NOT NULL | Title of the content |
| content_type | TEXT |  | Type of content (article, video) |
| content_url | TEXT |  | URL of the content (if external) or path to stored content |
| category | TEXT[] |  | Categories the content belongs to (e.g., nutrition, exercise, motivation) |
| tags | TEXT[] |  | Tags associated with the content |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT now() | Timestamp of content creation |

**Scalability Considerations:**

* **Horizontal Scaling:** Supabase (built on PostgreSQL) allows for horizontal scaling using read replicas and partitioning.
* **Indexing:** Create appropriate indexes on frequently queried columns (e.g., `user_id`, `workout_date`) to improve query performance.
* **JSONB:**  Using JSONB for flexible data like `dietary_preferences` and `meals` allows for efficient storage and querying of complex data structures.
* **Arrays:**  Using arrays for `fitness_goals`, `muscle_group`, and `equipment` allows for efficient storage and querying of multiple values.
* **Supabase Storage:** Store images and videos in Supabase Storage, which is designed for scalability and reliability.
* **Background Jobs:**  Use Supabase Functions to offload long-running tasks (e.g., video processing, AI inference) to background jobs.

This schema provides a solid foundation for a scalable fitness app. Remember to regularly monitor database performance and optimize as needed as your user base grows.