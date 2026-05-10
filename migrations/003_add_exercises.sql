-- Migration 003: Add lesson_id + explanation to exercises, create user_exercise_progress

-- Add lesson_id to exercises
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS lesson_id UUID;
ALTER TABLE exercises ADD CONSTRAINT fk_exercises_lesson
    FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE;

-- Make topic_id nullable (exercises are now lesson-scoped)
ALTER TABLE exercises ALTER COLUMN topic_id DROP NOT NULL;

-- Add explanation to exercises
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS explanation TEXT;

-- Create user_exercise_progress table
CREATE TABLE IF NOT EXISTS user_exercise_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    lesson_id UUID NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    exercise_id UUID NOT NULL REFERENCES exercises(id) ON DELETE CASCADE,
    correct BOOLEAN DEFAULT FALSE,
    attempts INTEGER DEFAULT 0,
    last_answer TEXT,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (user_id, exercise_id)
);

-- Create index for fast lookups
CREATE INDEX IF NOT EXISTS idx_uep_user_lesson ON user_exercise_progress(user_id, lesson_id);
