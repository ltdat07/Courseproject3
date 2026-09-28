import type { TopicSummary } from "../types";
import PixelIcon, { type PixelIconName } from "./PixelIcon";

const chapterIcons: PixelIconName[] = [
  "book", "flask", "key", "scroll", "shield",
  "sword", "gem", "chest", "tower", "crown",
];

type Props = {
  topics: TopicSummary[];
  completedTopicIds: number[];
  unlockedTopicIds: number[];
  isLoadingTopics: boolean;
  loadingTopicId: number | null;
  openTopic: (topicId: number) => void;
};

export default function TopicCatalog({
  topics,
  completedTopicIds,
  unlockedTopicIds,
  isLoadingTopics,
  loadingTopicId,
  openTopic,
}: Props) {
  return (
    <section className="levels-section">
      <div className="section-heading levels-heading">
        <div>
          <span className="section-kicker">Карта приключения</span>
          <h2>Выбери следующую главу</h2>
          <p>
            Главы открываются по порядку. К пройденным можно вернуться для повторения.
          </p>
        </div>

        <div className="chapters-counter">
          <strong>{completedTopicIds.length}</strong>
          <span>из {isLoadingTopics ? "…" : topics.length} глав</span>
        </div>
      </div>

      {isLoadingTopics && <p>Загрузка тем...</p>}
      {loadingTopicId !== null && <p role="status">Загрузка главы…</p>}

      {!isLoadingTopics && topics.length === 0 && (
        <p>Темы пока не найдены.</p>
      )}

      <div className="topics-grid">
        {topics.map((topic) => {
          const isCompleted = completedTopicIds.includes(topic.id);
          const isLocked = !unlockedTopicIds.includes(topic.id);
          const isLoading = loadingTopicId === topic.id;

          return (
            <article
              className={`topic-card${isCompleted ? " completed" : ""}${isLocked ? " locked" : ""}`}
              key={topic.id}
              onClick={() => {
                if (!isLocked && !isLoading) {
                  openTopic(topic.id);
                }
              }}
              onKeyDown={(event) => {
                if (
                  !isLocked && !isLoading &&
                  (event.key === "Enter" || event.key === " ")
                ) {
                  event.preventDefault();
                  openTopic(topic.id);
                }
              }}
              role="button"
              tabIndex={isLocked ? -1 : 0}
              aria-disabled={isLocked || isLoading}
              aria-busy={isLoading}
              aria-label={
                isLocked
                  ? `Глава ${topic.level} закрыта`
                  : `Открыть уровень ${topic.level}: ${topic.title}`
              }
            >
              <div className="topic-card-top">
                <span className="topic-icon" aria-hidden="true">
                  <PixelIcon
                    name={chapterIcons[Math.max(0, topic.level - 1) % chapterIcons.length]}
                    size={48}
                  />
                </span>

                <span
                  className={
                    isCompleted
                      ? "topic-status completed-status"
                      : isLocked
                        ? "topic-status locked-status"
                        : "topic-status"
                  }
                >
                  {isLoading
                    ? "Загрузка…"
                    : isCompleted
                      ? "Пройдено"
                      : isLocked
                        ? "Закрыто"
                        : "Доступно"}
                </span>
              </div>

              <span className="level">Глава {topic.level}</span>
              <span className="topic-subject">{topic.title}</span>
              <h3>{topic.quest_title ?? topic.title}</h3>
              <p>{topic.description}</p>

              <div className="topic-card-footer">
                <div className="topic-reward">
                  <span>Награда</span>
                  <strong>+{topic.points} XP</strong>
                </div>

                <span className="topic-arrow" aria-hidden="true">
                  <PixelIcon name={isLocked ? "lock" : "arrow"} size={24} />
                </span>
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}
