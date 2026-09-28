import type { TopicAnalytics, UserAnalytics } from "../types";
import { formatAttemptDate } from "../labels";

type Props = {
  analytics: UserAnalytics | null;
  isLoadingAnalytics: boolean;
  analyticsError: string | null;
  weakTopicAnalytics: TopicAnalytics[];
  attemptedTopicAnalytics: TopicAnalytics[];
};

export default function AnalyticsPanel({
  analytics,
  isLoadingAnalytics,
  analyticsError,
  weakTopicAnalytics,
  attemptedTopicAnalytics,
}: Props) {
  return (
    <section className="analytics-box">
      <div className="section-heading">
        <div>
          <span className="section-kicker">Результаты обучения</span>
          <h2>Аналитика прогресса</h2>
          <p>
            Здесь видны последние ответы и темы, которые стоит повторить.
          </p>
        </div>

        <div className="analytics-score">
          <strong>{analytics ? `${analytics.accuracy_percent}%` : "—"}</strong>
          <span>общая точность</span>
        </div>
      </div>

      {isLoadingAnalytics && (
        <p className="analytics-placeholder">Загружаем результаты...</p>
      )}

      {analyticsError && <p className="analytics-error">{analyticsError}</p>}

      {analytics && !isLoadingAnalytics && (
        <>
          <div className="analytics-summary">
            <article className="analytics-stat">
              <span>Всего ответов</span>
              <strong>{analytics.total_answers}</strong>
            </article>
            <article className="analytics-stat">
              <span>Правильных</span>
              <strong>{analytics.correct_answers}</strong>
            </article>
            <article className="analytics-stat">
              <span>Слабых тем</span>
              <strong>{analytics.weak_topic_count}</strong>
            </article>
          </div>

          <div className="analytics-columns">
            <div className="analytics-panel">
              <div className="analytics-panel-heading">
                <span aria-hidden="true">⚠</span>
                <h3>Слабые темы</h3>
              </div>

              {analytics.total_answers === 0 ? (
                <p className="analytics-empty">
                  Ответь на первое задание, чтобы увидеть результаты.
                </p>
              ) : weakTopicAnalytics.length === 0 ? (
                <p className="analytics-empty analytics-good">
                  Пока нет тем, требующих повторения.
                </p>
              ) : (
                <div className="weak-topics-list">
                  {weakTopicAnalytics.map((topic) => (
                    <article className="weak-topic" key={topic.topic_id}>
                      <div>
                        <strong>{topic.title}</strong>
                        <span>{topic.recommendation}</span>
                      </div>
                      <b>{topic.accuracy_percent}%</b>
                    </article>
                  ))}
                </div>
              )}
            </div>

            <div className="analytics-panel">
              <div className="analytics-panel-heading">
                <span aria-hidden="true">↻</span>
                <h3>Последние попытки</h3>
              </div>

              {analytics.recent_attempts.length === 0 ? (
                <p className="analytics-empty">История пока пуста.</p>
              ) : (
                <div className="attempt-history">
                  {analytics.recent_attempts.slice(0, 5).map((attempt) => (
                    <article className="attempt-history-item" key={attempt.id}>
                      <span
                        className={`attempt-result ${attempt.is_correct ? "correct" : "wrong"}`}
                        aria-label={
                          attempt.is_correct
                            ? "Правильный ответ"
                            : "Неправильный ответ"
                        }
                      >
                        {attempt.is_correct ? "✓" : "×"}
                      </span>
                      <div>
                        <strong>{attempt.topic_title}</strong>
                        <p>{attempt.question}</p>
                      </div>
                      <time dateTime={attempt.created_at}>
                        {formatAttemptDate(attempt.created_at)}
                      </time>
                    </article>
                  ))}
                </div>
              )}
            </div>
          </div>

          {attemptedTopicAnalytics.length > 0 && (
            <div className="topic-analytics-list">
              {attemptedTopicAnalytics.map((topic) => (
                <article
                  className={`topic-analytics-item${topic.is_weak ? " weak" : ""}`}
                  key={topic.topic_id}
                >
                  <div className="topic-analytics-heading">
                    <strong>{topic.title}</strong>
                    <span>{topic.accuracy_percent}%</span>
                  </div>
                  <div className="topic-accuracy-track" aria-hidden="true">
                    <span
                      style={{ width: `${topic.accuracy_percent}%` }}
                    />
                  </div>
                  <p>
                    {topic.correct_answers} правильных из {topic.total_answers}
                  </p>
                </article>
              ))}
            </div>
          )}
        </>
      )}
    </section>
  );
}
