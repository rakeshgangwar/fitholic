export interface Exercise {
  exercise_id: string;
  name: string;
  description?: string;
  muscle_groups: string[];
  equipment: string[];
  difficulty?: string;
  instructions?: string;
  video_url?: string;
  created_at: string;
  updated_at: string;
}

export interface TemplateExercise {
  exercise_id: string;
  sets: number;
  reps: number;
  rest_time: number;
}

export interface WorkoutTemplate {
  template_id: string;
  name: string;
  description?: string;
  difficulty: string;
  exercises: TemplateExercise[];
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface WorkoutSetLog {
  reps: number;
  weight?: number;
  completed: boolean;
}

export interface WorkoutExerciseLog {
  exercise_id: string;
  sets: WorkoutSetLog[];
}

export interface WorkoutLog {
  log_id: string;
  user_id: string;
  template_id?: string;
  start_time: string;
  end_time?: string;
  date: string;
  duration?: number;
  notes?: string;
  status: 'scheduled' | 'ongoing' | 'completed';
  exercises: WorkoutExerciseLog[];
  created_at: string;
  updated_at: string;
}

export interface NotificationSettings {
    workout_reminders: boolean;
    progress_updates: boolean;
    achievement_alerts: boolean;
}

export interface PrivacySettings {
    profile_visibility: 'public' | 'private' | 'friends';
    share_workouts: boolean;
    share_progress: boolean;
}

export interface UserProfile {
    id: string;
    user_id: string;
    height?: number;
    weight?: number;
    date_of_birth?: string;
    gender?: string;
    fitness_goals?: string[];
    preferred_workout_duration?: number;
    preferred_workout_days?: string[];
    available_equipment?: string[];
    theme: 'light' | 'dark' | 'system';
    language: string;
    units: 'metric' | 'imperial';
    notification_settings: NotificationSettings;
    privacy_settings: PrivacySettings;
    created_at: string;
    updated_at: string;
}

export interface UserProfileUpdate {
    height?: number;
    weight?: number;
    date_of_birth?: string;
    gender?: string;
    fitness_goals?: string[];
    preferred_workout_duration?: number;
    preferred_workout_days?: string[];
    available_equipment?: string[];
    theme?: 'light' | 'dark' | 'system';
    language?: string;
    units?: 'metric' | 'imperial';
    notification_settings?: NotificationSettings;
    privacy_settings?: PrivacySettings;
} 