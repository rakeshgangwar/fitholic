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
  date: string;
  duration?: number;
  notes?: string;
  exercises: WorkoutExerciseLog[];
  created_at: string;
  updated_at: string;
} 