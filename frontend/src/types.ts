export type CurrentUser = {
  id: number;
  username: string;
  display_name: string | null;
  total_xp: number;
};

export type TopicSummary = {
  id: number;
  title: string;
  quest_title: string;
  description: string;
  level: number;
  points: number;
};

export type TopicDetail = TopicSummary & {
  theory: string;
  achievement: string | null;
};

export type TaskOption = {
  id: number;
  text: string;
};

export type Task = {
  id: number;
  topic_id: number;
  story: string;
  question: string;
  type: string;
  code?: string | null;
  options: TaskOption[];
};

export type AnswerResult = {
  is_correct: boolean;
  message: string;
  explanation: string;
  earned_points: number;
  total_xp: number;
  topic_completed: boolean;
  achievement_unlocked?: string | null;
  unlocked_topic_id?: number | null;
};

export type ProgressAchievement = {
  id: number;
  title: string;
};

export type UserProgress = {
  total_xp: number;
  unlocked_topic_ids: number[];
  completed_topic_ids: number[];
  achievements: ProgressAchievement[];
};

export type TopicAnalytics = {
  topic_id: number;
  title: string;
  total_answers: number;
  correct_answers: number;
  accuracy_percent: number;
  is_weak: boolean;
  recommendation?: string | null;
};

export type AttemptHistoryItem = {
  id: number;
  task_id: number;
  topic_id: number;
  topic_title: string;
  question: string;
  selected_option_id?: number | null;
  is_correct: boolean;
  earned_points: number;
  created_at: string;
};

export type UserAnalytics = {
  total_answers: number;
  correct_answers: number;
  accuracy_percent: number;
  weak_topic_count: number;
  topics: TopicAnalytics[];
  recent_attempts: AttemptHistoryItem[];
};

export type AiFeedbackStatus = {
  available: boolean;
  provider: string;
  model?: string | null;
  message: string;
};

export type AiPractice = {
  id: string;
  topic_title: string;
  title: string;
  story: string;
  assignment: string;
  starter_code: string;
};

export type AiFeedback = {
  verdict: "correct" | "partially_correct" | "needs_revision";
  summary: string;
  strengths: string[];
  issues: string[];
  hints: string[];
  suggested_fragment?: string | null;
  model: string;
};
