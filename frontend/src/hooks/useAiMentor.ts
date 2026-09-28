import { useCallback, useEffect, useState } from "react";
import { fetchAiPractices, fetchAiStatus, requestAiFeedback } from "../api";
import type { ApiRequest } from "../api";
import type { AiFeedbackStatus, AiPractice, AiFeedback } from "../types";
import { loadAiDraft, restoreAiDraft, saveAiDraft } from "../aiDraft";
import type { AiDraft } from "../aiDraft";
import { prepareAiPracticeChange } from "../aiPracticeSelection";

export default function useAiMentor(request: ApiRequest, userId: number) {
  const [aiStatus, setAiStatus] = useState<AiFeedbackStatus | null>(null);
  const [aiStatusRefreshToken, setAiStatusRefreshToken] = useState(0);
  const [aiCatalogRefreshToken, setAiCatalogRefreshToken] = useState(0);
  const [isCheckingAiStatus, setIsCheckingAiStatus] = useState(true);
  const [aiPractices, setAiPractices] = useState<AiPractice[]>([]);
  const [initialAiDraft] = useState(() => loadAiDraft(userId));
  const [aiDraft, setAiDraft] = useState(initialAiDraft);
  const [isAiDraftSaved, setIsAiDraftSaved] = useState(true);
  const selectedAiPracticeId = aiDraft?.practiceId ?? null;
  const studentSolution = aiDraft?.studentSolution ?? "";
  const aiFeedback = aiDraft?.feedback ?? null;
  const [aiError, setAiError] = useState<string | null>(null);
  const [isAiLabOpen, setIsAiLabOpen] = useState(Boolean(initialAiDraft));
  const [isAnalyzingSolution, setIsAnalyzingSolution] = useState(false);
  const [cloudReviewConsent, setCloudReviewConsent] = useState(false);

  const updateAiDraft = useCallback((draft: AiDraft) => {
    setAiDraft(draft);
    setIsAiDraftSaved(saveAiDraft(draft, userId));
  }, [userId]);

  useEffect(() => {
    let isCancelled = false;

    fetchAiPractices(request)
      .then((practicesData: AiPractice[]) => {
        if (isCancelled) {
          return;
        }

        setAiPractices(practicesData);

        const restored = restoreAiDraft(practicesData, initialAiDraft);
        if (restored) updateAiDraft(restored);
      })
      .catch(() => {
        if (!isCancelled) {
          setAiError("Не удалось загрузить испытания. Запусти backend и нажми «Проверить связь».");
        }
      });

    return () => {
      isCancelled = true;
    };
  }, [aiCatalogRefreshToken, initialAiDraft, updateAiDraft, request]);

  useEffect(() => {
    let isCancelled = false;

    fetchAiStatus(request)
      .then((data: AiFeedbackStatus) => {
        if (!isCancelled) setAiStatus(data);
      })
      .catch(() => {
        if (!isCancelled) {
          setAiStatus({
            available: false,
            provider: "Groq",
            message: "Не удалось связаться с сервером тренажёра. Запусти backend и проверь связь снова.",
          });
        }
      })
      .finally(() => {
        if (!isCancelled) setIsCheckingAiStatus(false);
      });

    return () => { isCancelled = true; };
  }, [aiStatusRefreshToken, request]);

  const selectAiPractice = (practice: AiPractice) => {
    if (isAnalyzingSolution) return;
    const nextDraft = prepareAiPracticeChange(practice, aiDraft, currentAiPractice, () => window.confirm(
      `Открыть испытание «${practice.title}»? Текущий код и разбор будут заменены. ` +
      "Если они нужны, нажми «Отмена» и скопируй их перед переходом.",
    ));
    if (!nextDraft) return;
    updateAiDraft(nextDraft);
    setCloudReviewConsent(false);
    setAiError(null);
  };

  const refreshAiConnection = () => {
    setIsCheckingAiStatus(true);
    setAiError(null);
    setAiStatusRefreshToken((prev) => prev + 1);
    if (aiPractices.length === 0) {
      setAiCatalogRefreshToken((prev) => prev + 1);
    }
  };

  const analyzeStudentSolution = async () => {
    if (
      !aiDraft || !selectedAiPracticeId ||
      studentSolution.trim().length < 12 ||
      isAnalyzingSolution ||
      isCheckingAiStatus ||
      !cloudReviewConsent ||
      !aiStatus?.available
    ) {
      return;
    }

    try {
      setIsAnalyzingSolution(true);
      setAiError(null);

      const response = await requestAiFeedback(request, selectedAiPracticeId, studentSolution);

      if (!response.ok) {
        const payload = await response.json().catch(() => null);
        const detail =
          payload && typeof payload.detail === "string"
            ? payload.detail
            : "ИИ-наставник не смог разобрать решение.";
        if (response.status === 503) {
          setAiStatus((prev) => ({
            ...prev, provider: "Groq", available: false, message: detail,
          }));
        }
        throw new Error(detail);
      }

      const data: AiFeedback = await response.json();
      updateAiDraft({ ...aiDraft, feedback: data });
    } catch (error) {
      setAiError(
        error instanceof Error && error.name === "TimeoutError"
          ? "Облачный разбор занял слишком много времени. Повтори попытку позже."
          : error instanceof TypeError
            ? "Связь с сервером прервалась. Проверь backend и повтори разбор."
            : error instanceof Error
              ? error.message
              : "ИИ-наставник не смог разобрать решение.",
      );
    } finally {
      setIsAnalyzingSolution(false);
    }
  };

  const currentAiPractice =
    aiPractices.find((practice) => practice.id === selectedAiPracticeId) ?? null;

  return {
    aiStatus,
    isCheckingAiStatus,
    refreshAiConnection,
    isAnalyzingSolution,
    setIsAiLabOpen,
    aiPractices,
    isAiLabOpen,
    aiError,
    currentAiPractice,
    selectedAiPracticeId,
    selectAiPractice,
    isAiDraftSaved,
    studentSolution,
    aiDraft,
    updateAiDraft,
    setAiError,
    cloudReviewConsent,
    setCloudReviewConsent,
    analyzeStudentSolution,
    aiFeedback,
  };
}
