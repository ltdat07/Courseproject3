import { useEffect, useState } from "react";
import { fetchAnalytics } from "../api";
import type { ApiRequest } from "../api";
import type { UserAnalytics } from "../types";

export default function useAnalytics(request: ApiRequest, answerRevision: number) {
  const [analytics, setAnalytics] = useState<UserAnalytics | null>(null);
  const [isLoadingAnalytics, setIsLoadingAnalytics] = useState(true);
  const [analyticsError, setAnalyticsError] = useState<string | null>(null);

  useEffect(() => {
    let isCancelled = false;

    fetchAnalytics(request)
      .then((data: UserAnalytics) => {
        if (!isCancelled) {
          setAnalytics(data);
          setAnalyticsError(null);
        }
      })
      .catch(() => {
        if (!isCancelled) {
          setAnalyticsError("Оракул временно не смог прочитать историю попыток.");
        }
      })
      .finally(() => {
        if (!isCancelled) {
          setIsLoadingAnalytics(false);
        }
      });

    return () => {
      isCancelled = true;
    };
  }, [answerRevision, request]);

  const attemptedTopicAnalytics =
    analytics?.topics.filter((topic) => topic.total_answers > 0) ?? [];
  const weakTopicAnalytics =
    analytics?.topics.filter((topic) => topic.is_weak) ?? [];

  return {
    analytics,
    isLoadingAnalytics,
    analyticsError,
    attemptedTopicAnalytics,
    weakTopicAnalytics,
  };
}
