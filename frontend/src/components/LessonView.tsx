import type { AnswerResult, Task, TopicDetail } from "../types";
import { getTaskTypeLabel } from "../labels";
import TheoryContent from "./TheoryContent";
import CodePanel from "./CodePanel";
import PixelIcon from "./PixelIcon";

type Props = {
  selectedTopic: TopicDetail;
  currentTask: Task | undefined;
  goBackToTopics: () => void;
  currentTaskIndex: number;
  tasks: Task[];
  selectedOptionId: number | null;
  setSelectedOptionId: (optionId: number) => void;
  answerResult: AnswerResult | null;
  checkAnswer: (taskId: number) => void;
  isCheckingAnswer: boolean;
  retryTask: () => void;
  isLastTask: boolean;
  goToNextTask: () => void;
};

export default function LessonView({
  selectedTopic,
  currentTask,
  goBackToTopics,
  currentTaskIndex,
  tasks,
  selectedOptionId,
  setSelectedOptionId,
  answerResult,
  checkAnswer,
  isCheckingAnswer,
  retryTask,
  isLastTask,
  goToNextTask,
}: Props) {
  return (
    <>
    {selectedTopic && !currentTask && (
      <section className="level-page">
        <button className="back-button" onClick={goBackToTopics}>
          ← Назад к уровням
        </button>

        <span className="chapter-eyebrow">
          Глава {selectedTopic.level} · {selectedTopic.quest_title ?? selectedTopic.title}
        </span>
        <h2>{selectedTopic.title}</h2>
        <p>В этой теме пока нет заданий.</p>
      </section>
    )}

    {selectedTopic && currentTask && (
      <section className="level-page">
        <button className="back-button" onClick={goBackToTopics}>
          ← Назад к уровням
        </button>

        <div className="level-header">
          <div>
            <span className="chapter-eyebrow">
              Глава {selectedTopic.level} · {selectedTopic.quest_title ?? selectedTopic.title}
            </span>
            <h2>{selectedTopic.title}</h2>

            <p>
              Задание {currentTaskIndex + 1} из {tasks.length}
            </p>
          </div>

          <span className="level-progress">
            {Math.round(((currentTaskIndex + 1) / tasks.length) * 100)}%
          </span>
        </div>

        <div className="theory-box">
          <div className="theory-heading">
            <div>
              <span>Справочник главы</span>
              <h3>Свиток теории</h3>
            </div>
            <b>Пример · ошибки · вывод</b>
          </div>

          <TheoryContent theory={selectedTopic.theory} />
        </div>

        <div className="task-box">
          <span className="task-type">
            {getTaskTypeLabel(currentTask.type)}
          </span>

          <p className="story">{currentTask.story}</p>

          {currentTask.code && (
            <CodePanel title="Фрагмент кода" code={currentTask.code} />
          )}

          <h3>{currentTask.question}</h3>

          <div className="options">
            {currentTask.options.map((option) => (
              <button
                key={option.id}
                className={
                  selectedOptionId === option.id
                    ? "option selected"
                    : "option"
                }
                onClick={() => setSelectedOptionId(option.id)}
                disabled={answerResult !== null || isCheckingAnswer}
              >
                {option.text}
              </button>
            ))}
          </div>

          <button
            className="check-button"
            onClick={() => checkAnswer(currentTask.id)}
            disabled={
              selectedOptionId === null || answerResult !== null || isCheckingAnswer
            }
          >
            {isCheckingAnswer ? "Проверяем..." : "Проверить ответ"}
          </button>

          {answerResult && (
            <div
              className={answerResult.is_correct ? "result success" : "result error"}
            >
              <h3>{answerResult.is_correct ? "Правильно!" : "Ошибка!"}</h3>

              <p>{answerResult.message}</p>
              <p>{answerResult.explanation}</p>

              <strong>Получено XP: {answerResult.earned_points}</strong>

              {answerResult.achievement_unlocked && (
                <p className="result-achievement"><PixelIcon name="crown" /> Открыто достижение: {answerResult.achievement_unlocked}</p>
              )}

              <div>
                {!answerResult.is_correct ? (
                  <button className="next-button" onClick={retryTask}>
                    Попробовать ещё раз
                  </button>
                ) : !isLastTask ? (
                  <button className="next-button" onClick={goToNextTask}>
                    Следующее задание →
                  </button>
                ) : (
                  <button className="next-button" onClick={goBackToTopics}>
                    Завершить уровень
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      </section>
    )}
    </>
  );
}
