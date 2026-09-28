import type {
  AiFeedbackStatus, AiPractice, AnswerResult, Task, TopicSummary, TopicDetail,
  UserAnalytics, UserProgress,
} from "./types";

export const API_BASE_URL = "/api";

export async function apiFetch(url: string, options: RequestInit = {}, userId?: number): Promise<Response> {
  const headers = new Headers(options.headers);
  if (options.method && !["GET", "HEAD", "OPTIONS"].includes(options.method.toUpperCase())) {
    headers.set("X-Trainer-Request", "1");
  }
  if (userId !== undefined) headers.set("X-Trainer-User", String(userId));
  const response = await fetch(url, {
    ...options, headers, credentials: "same-origin", cache: "no-store",
    signal: options.signal ?? AbortSignal.timeout(15_000),
  });
  if (response.status === 401 && !url.includes("/auth/login")) {
    window.dispatchEvent(new Event("trainer:unauthorized"));
  }
  return response;
}

export type ApiRequest = (url: string, options?: RequestInit) => Promise<Response>;

async function readJson<T>(response: Response, errorMessage: string): Promise<T> {
  if (!response.ok) throw new Error(errorMessage);
  return response.json() as Promise<T>;
}

export async function fetchTopics(request: ApiRequest): Promise<TopicSummary[]> {
  return readJson(await request(`${API_BASE_URL}/topics/`), "Failed to load topics");
}

export async function fetchTopic(request: ApiRequest, topicId: number): Promise<TopicDetail> {
  return readJson(await request(`${API_BASE_URL}/topics/${topicId}`), "Failed to load topic");
}

export async function fetchTasks(request: ApiRequest, topicId: number): Promise<Task[]> {
  return readJson(await request(`${API_BASE_URL}/topics/${topicId}/tasks`), "Failed to load tasks");
}

export async function fetchProgress(request: ApiRequest): Promise<UserProgress> {
  return readJson(await request(`${API_BASE_URL}/users/me/progress`), "Failed to load user profile");
}

export async function fetchAnalytics(request: ApiRequest): Promise<UserAnalytics> {
  return readJson(await request(`${API_BASE_URL}/users/me/analytics`), "Failed to load analytics");
}

export async function submitAnswer(
  request: ApiRequest, taskId: number, selectedOptionId: number,
): Promise<AnswerResult> {
  const response = await request(`${API_BASE_URL}/topics/tasks/${taskId}/check`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ selected_option_id: selectedOptionId }),
  });
  return readJson(response, "Failed to check answer");
}

export async function fetchAiPractices(request: ApiRequest): Promise<AiPractice[]> {
  const response = await request(`${API_BASE_URL}/ai-feedback/practices`, {
    signal: AbortSignal.timeout(7000),
  });
  return readJson(response, "Failed to load AI practices");
}

export async function fetchAiStatus(request: ApiRequest): Promise<AiFeedbackStatus> {
  const response = await request(`${API_BASE_URL}/ai-feedback/status`, {
    signal: AbortSignal.timeout(7000),
  });
  return readJson(response, "Failed to check AI status");
}

export function requestAiFeedback(
  request: ApiRequest, practiceId: string, studentSolution: string,
): Promise<Response> {
  return request(`${API_BASE_URL}/ai-feedback/analyze`, {
    method: "POST",
    signal: AbortSignal.timeout(70_000),
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ practice_id: practiceId, student_solution: studentSolution }),
  });
}
