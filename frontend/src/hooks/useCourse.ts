import { useEffect, useRef, useState } from "react";
import { fetchTopics, fetchProgress, fetchTopic, fetchTasks, submitAnswer } from "../api";
import type { ApiRequest } from "../api";
import type { TopicSummary, TopicDetail, Task, AnswerResult, UserProgress } from "../types";

export default function useCourse(request: ApiRequest) {
  const [topics, setTopics] = useState<TopicSummary[]>([]);
  const [selectedTopic, setSelectedTopic] = useState<TopicDetail | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [currentTaskIndex, setCurrentTaskIndex] = useState(0);
  const [selectedOptionId, setSelectedOptionIdState] = useState<number | null>(null);
  const [answerResult, setAnswerResult] = useState<AnswerResult | null>(null);
  const [isCheckingAnswer, setIsCheckingAnswer] = useState(false);
  const answerPending = useRef(false);
  const viewVersion = useRef(0);
  const requestVersion = useRef(0);

  useEffect(() => () => {
    viewVersion.current += 1;
    requestVersion.current += 1;
    answerPending.current = false;
  }, [request]);

  const [totalXp, setTotalXp] = useState(0);
  const [achievements, setAchievements] = useState<string[]>([]);
  const [completedTopicIds, setCompletedTopicIds] = useState<number[]>([]);
  const [unlockedTopicIds, setUnlockedTopicIds] = useState<number[]>([1]);
  const [answerRevision, setAnswerRevision] = useState(0);
  const [isLoadingTopics, setIsLoadingTopics] = useState(true);
  const [loadingTopicId, setLoadingTopicId] = useState<number | null>(null);
  const [courseError, setCourseError] = useState<string | null>(null);

  useEffect(() => {
    let isCancelled = false;

    fetchTopics(request)
      .then((data) => {
        if (!isCancelled) {
          setTopics(data);
        }
      })
      .catch(() => {
        if (!isCancelled) {
          setCourseError(
            "Не удалось загрузить темы. Проверь, запущен ли backend.",
          );
        }
      })
      .finally(() => {
        if (!isCancelled) {
          setIsLoadingTopics(false);
        }
      });

    return () => {
      isCancelled = true;
    };
  }, [request]);

  useEffect(() => {
    let isCancelled = false;

    fetchProgress(request)
      .then((data: UserProgress) => {
        if (!isCancelled) {
          // Начальная загрузка может завершиться уже после первого ответа.
          setTotalXp((prev) => Math.max(prev, data.total_xp));
          setUnlockedTopicIds((prev) => [...new Set([...prev, ...data.unlocked_topic_ids])]);
          setCompletedTopicIds((prev) => [...new Set([...prev, ...data.completed_topic_ids])]);
          setAchievements((prev) => [...new Set([
            ...prev, ...data.achievements.map((achievement) => achievement.title),
          ])]);
        }
      })
      .catch(() => {
        if (!isCancelled) {
          setCourseError("Не удалось загрузить сохранённый прогресс героя.");
        }
      });

    return () => {
      isCancelled = true;
    };
  }, [request]);

  const openTopic = async (topicId: number) => {
    if (!unlockedTopicIds.includes(topicId)) {
      return;
    }

    const version = ++viewVersion.current;
    try {
      setLoadingTopicId(topicId);
      setCourseError(null);
      setSelectedTopic(null);
      setTasks([]);
      setSelectedOptionIdState(null);
      setAnswerResult(null);
      setCurrentTaskIndex(0);

      const [topicData, tasksData] = await Promise.all([
        fetchTopic(request, topicId), fetchTasks(request, topicId),
      ]);
      if (version !== viewVersion.current) return;

      setSelectedTopic(topicData);
      setTasks(tasksData);
    } catch {
      if (version === viewVersion.current) {
        setCourseError("Не удалось открыть тему. Проверь backend.");
      }
    } finally {
      if (version === viewVersion.current) setLoadingTopicId(null);
    }
  };

  const checkAnswer = async (taskId: number) => {
    if (selectedOptionId === null || answerResult !== null || answerPending.current
      || tasks[currentTaskIndex]?.id !== taskId) {
      return;
    }

    const version = viewVersion.current;
    const currentRequest = requestVersion.current;
    answerPending.current = true;
    try {
      setCourseError(null);
      setIsCheckingAnswer(true);

      const data = await submitAnswer(request, taskId, selectedOptionId);
      if (currentRequest !== requestVersion.current) return;

      // Прогресс обновляется всегда, результат задания — только в прежнем уроке.
      if (version === viewVersion.current) setAnswerResult(data);
      setTotalXp(data.total_xp);
      setAnswerRevision((prev) => prev + 1);

      if (data.topic_completed && selectedTopic) {
        setCompletedTopicIds((prev) =>
          prev.includes(selectedTopic.id) ? prev : [...prev, selectedTopic.id],
        );
      }

      if (data.unlocked_topic_id) {
        setUnlockedTopicIds((prev) =>
          prev.includes(data.unlocked_topic_id as number)
            ? prev
            : [...prev, data.unlocked_topic_id as number],
        );
      }

      if (data.achievement_unlocked) {
        setAchievements((prev) =>
          prev.includes(data.achievement_unlocked as string)
            ? prev
            : [...prev, data.achievement_unlocked as string],
        );
      }
    } catch {
      if (version === viewVersion.current && currentRequest === requestVersion.current) {
        setCourseError("Не удалось проверить ответ. Проверь backend.");
      }
    } finally {
      if (currentRequest === requestVersion.current) {
        answerPending.current = false;
        setIsCheckingAnswer(false);
      }
    }
  };

  const setSelectedOptionId = (optionId: number) => {
    if (!answerPending.current && answerResult === null) setSelectedOptionIdState(optionId);
  };

  const goToNextTask = () => {
    if (answerPending.current || !answerResult?.is_correct || currentTaskIndex >= tasks.length - 1) return;
    viewVersion.current += 1;
    setCurrentTaskIndex((prev) => prev + 1);
    setSelectedOptionIdState(null);
    setAnswerResult(null);
  };

  const retryTask = () => {
    if (answerPending.current) return;
    viewVersion.current += 1;
    setSelectedOptionIdState(null);
    setAnswerResult(null);
  };

  const goBackToTopics = () => {
    viewVersion.current += 1;
    setLoadingTopicId(null);
    setSelectedTopic(null);
    setTasks([]);
    setCurrentTaskIndex(0);
    setSelectedOptionIdState(null);
    setAnswerResult(null);
  };

  const currentTask = tasks[currentTaskIndex];
  const isLastTask = currentTaskIndex === tasks.length - 1;
  const learningProgress = topics.length
    ? Math.round((completedTopicIds.length / topics.length) * 100)
    : 0;
  const isCourseCompleted =
    topics.length > 0 && completedTopicIds.length === topics.length;
  const nextLevelNumber =
    (topics.find((topic) => !completedTopicIds.includes(topic.id))?.level ??
      topics.length) || 1;

  return {
    topics,
    selectedTopic,
    tasks,
    currentTaskIndex,
    selectedOptionId,
    setSelectedOptionId,
    answerResult,
    isCheckingAnswer,
    totalXp,
    achievements,
    completedTopicIds,
    unlockedTopicIds,
    answerRevision,
    isLoadingTopics,
    loadingTopicId,
    courseError,
    openTopic,
    checkAnswer,
    goToNextTask,
    retryTask,
    goBackToTopics,
    currentTask,
    isLastTask,
    learningProgress,
    isCourseCompleted,
    nextLevelNumber,
  };
}
