import type { TopicSummary } from "../types";
import PixelIcon from "./PixelIcon";

type Props = {
  totalXp: number;
  achievements: string[];
  completedTopicIds: number[];
  learningProgress: number;
  isLoadingTopics: boolean;
  topics: TopicSummary[];
  isCourseCompleted: boolean;
  nextLevelNumber: number;
};

export default function HeroSummary({
  totalXp,
  achievements,
  completedTopicIds,
  learningProgress,
  isLoadingTopics,
  topics,
  isCourseCompleted,
  nextLevelNumber,
}: Props) {
  return (
    <section className="hero">
      <div className="hero-content">
        <div className="hero-kicker">
          <span className="hero-kicker-dot" aria-hidden="true" />
          Королевская академия кода
        </div>

        <h1>
          Интерактивный тренажер <span>C#</span>
        </h1>

        <div className="narrator-box">
          <span className="narrator-avatar" aria-hidden="true">
            <PixelIcon name="tower" size={48} />
          </span>
          <div>
            <span className="narrator-name">Архимаг Компилятор</span>
            <p className="hero-description">
              Изучай C# по главам: теория, задания и разбор ответов.
              За верные решения получай опыт, за пройденные главы — достижения.
            </p>
          </div>
        </div>

        <div className="stats-row">
          <div className="hero-stat">
            <span className="hero-stat-icon xp-icon" aria-hidden="true">
              <PixelIcon name="gem" />
            </span>
            <div>
              <span className="hero-stat-label">Опыт</span>
              <strong>{totalXp} XP</strong>
            </div>
          </div>

          <div className="hero-stat">
            <span
              className="hero-stat-icon achievement-icon"
              aria-hidden="true"
            >
              <PixelIcon name="crown" />
            </span>
            <div>
              <span className="hero-stat-label">Достижения</span>
              <strong>{achievements.length}</strong>
            </div>
          </div>

          <div className="hero-stat">
            <span className="hero-stat-icon level-icon" aria-hidden="true">
              <PixelIcon name="book" />
            </span>
            <div>
              <span className="hero-stat-label">Пройдено глав</span>
              <strong>{completedTopicIds.length}</strong>
            </div>
          </div>
        </div>
      </div>

      <aside className="hero-progress-card">
        <div className="hero-progress-header">
          <div>
            <span className="hero-progress-caption">Прогресс курса</span>
            <h2>Путь героя</h2>
          </div>

          <span className="hero-progress-percent">{learningProgress}%</span>
        </div>

        <div
          className="hero-progress-track"
          role="progressbar"
          aria-label="Прогресс обучения"
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={learningProgress}
        >
          <div
            className="hero-progress-fill"
            style={{ width: `${learningProgress}%` }}
          />
        </div>

        <div className="hero-progress-meta">
          <span>Завершено глав</span>
          <strong>
            {completedTopicIds.length} / {isLoadingTopics ? "…" : topics.length}
          </strong>
        </div>

        <div className="hero-mission">
          <span className="hero-mission-marker" aria-hidden="true">
            <PixelIcon name="sword" />
          </span>
          <div>
            <span>{isCourseCompleted ? "Итог" : "Следующая цель"}</span>
            <strong>
              {isCourseCompleted
                ? "Все главы пройдены!"
                : `Пройти главу ${nextLevelNumber}`}
            </strong>
          </div>
        </div>

        <p className="hero-progress-note">
          За первое верное решение — 10 XP.
        </p>
      </aside>
    </section>
  );
}
