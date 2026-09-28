import type { AiFeedback } from "./types";

export function getAiVerdictLabel(verdict: AiFeedback["verdict"]) {
  if (verdict === "correct") {
    return "Заклинание работает";
  }

  if (verdict === "partially_correct") {
    return "Почти готово к бою";
  }

  return "Свиток требует правки";
}

export function getTaskTypeLabel(type: string) {
  if (type === "single_choice") {
    return "Выбор ответа";
  }

  if (type === "code_output") {
    return "Что выведет код?";
  }

  if (type === "find_error") {
    return "Найди ошибку";
  }

  if (type === "choose_fix") {
    return "Выбери исправление";
  }

  return "Задание";
}

export function formatAttemptDate(value: string) {
  return new Intl.DateTimeFormat("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

export function getTopicIcon(topicId: number) {
  const icons: Record<number, string> = {
    1: "⌘",
    2: "⚖",
    3: "✦",
    4: "▦",
    5: "♜",
    6: "☠",
    7: "⌕",
    8: "⧖",
    9: "✎",
    10: "◈",
    11: "◇",
    12: "▤",
  };

  return icons[topicId] ?? "⌘";
}
