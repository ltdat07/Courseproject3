import type { Dispatch, SetStateAction } from "react";
import type { AiFeedback, AiFeedbackStatus, AiPractice } from "../types";
import type { AiDraft } from "../aiDraft";
import { getAiVerdictLabel } from "../labels";
import FeedbackList from "./FeedbackList";

type Props = {
  aiStatus: AiFeedbackStatus | null;
  isCheckingAiStatus: boolean;
  refreshAiConnection: () => void;
  isAnalyzingSolution: boolean;
  setIsAiLabOpen: Dispatch<SetStateAction<boolean>>;
  aiPractices: AiPractice[];
  isAiLabOpen: boolean;
  aiError: string | null;
  currentAiPractice: AiPractice | null;
  selectedAiPracticeId: string | null;
  selectAiPractice: (practice: AiPractice) => void;
  isAiDraftSaved: boolean;
  studentSolution: string;
  aiDraft: AiDraft | null;
  updateAiDraft: (draft: AiDraft) => void;
  setAiError: (error: string | null) => void;
  cloudReviewConsent: boolean;
  setCloudReviewConsent: (consent: boolean) => void;
  analyzeStudentSolution: () => void;
  aiFeedback: AiFeedback | null;
};

export default function AiMentor({
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
}: Props) {
  return (
    <section className="ai-lab-section">
      <div className="ai-lab-intro">
        <div className="ai-lab-emblem" aria-hidden="true">
          <svg
            viewBox="0 0 32 32"
            shapeRendering="crispEdges"
            focusable="false"
          >
            <path
              d="M4 0h24v2h2v2h2v24h-2v2h-2v2H4v-2H2v-2H0V4h2V2h2Z"
              fill="#926b38"
            />
            <path d="M4 0h24v2H4v2H2v24H0V4h2V2h2Z" fill="#c5a064" />
            <path d="M30 4h2v24h-2v2h-2v2H4v-2h24v-2h2Z" fill="#5a3e26" />
            <path d="M4 3h24v1h1v24h-1v1H4v-1H3V4h1Z" fill="#241c17" />
            <path d="M5 4h22v1h1v22h-1v1H5v-1H4V5h1Z" fill="#38291e" />
            <path
              d="M7 6h5v3h2V6h4v3h2V6h5v9h-2v9h2v4H7v-4h2v-9H7Z"
              fill="#1c1612"
            />
            <path
              d="M8 7h3v3h4V7h2v3h4V7h3v7h-2v11h2v2H8v-2h2V14H8Z"
              fill="#bc9557"
            />
            <path d="M8 7h3v1H9v4H8Zm7 0h2v1h-2Zm6 0h3v1h-3ZM10 15h2v10h-2Z" fill="#e3c685" />
            <path d="M22 8h2v6h-2Zm-2 7h2v10h-2ZM8 26h16v1H8Z" fill="#795431" />
            <path d="M8 12h16v1H8Zm2 2h12v1H10Z" fill="#e3c685" />
            <path d="M15 16h2v3h-2Zm-1 5h4v1h1v5h-6v-5h1Z" fill="#302219" />
            <path d="M14 23h1v4h-1Zm2-1h1v5h-1Z" fill="#704c2d" />
            <path d="M12 17h2v1h-2Zm6 3h2v1h-2Zm-6 3h1v1h-1ZM9 25h3v1H9Zm11 0h3v1h-3Z" fill="#99713e" />
          </svg>
        </div>

        <div className="ai-lab-copy">
          <span className="section-kicker">Дополнительная функция</span>
          <h2>Башня ИИ-наставника</h2>
          <p>
            Напиши решение на C# и получи разбор: что получилось
            и что можно исправить.
          </p>

          <div className="ai-lab-notes">
            <span>Не влияет на XP</span>
            <span>Код не запускается</span>
            <span>ИИ-подсказки</span>
          </div>
        </div>

        <div className="ai-lab-entry">
          <span
            className={`ai-status${aiStatus?.available ? " available" : ""}`}
            role="status"
          >
            <i aria-hidden="true" />
            {isCheckingAiStatus
              ? "Проверяем связь..."
              : aiStatus?.available
                ? "ИИ-наставник готов к разбору"
                : "Нет связи с наставником"}
          </span>
          <button
            className="ai-connection-button"
            onClick={refreshAiConnection}
            disabled={isCheckingAiStatus || isAnalyzingSolution}
          >
            Проверить связь
          </button>
          <button
            className="ai-lab-toggle"
            onClick={() => setIsAiLabOpen((prev) => !prev)}
            disabled={aiPractices.length === 0}
            aria-expanded={isAiLabOpen}
          >
            {isAiLabOpen ? "Закрыть лабораторию" : "Войти в лабораторию"}
          </button>
        </div>
      </div>

      {!isCheckingAiStatus && !aiStatus?.available && aiStatus?.message && (
        <p className="ai-connection-message" role="status">{aiStatus.message}</p>
      )}
      {aiError && <p className="ai-feedback-error" role="alert">{aiError}</p>}

      {isAiLabOpen && currentAiPractice && (
        <div className="ai-lab-panel">
          <div className="ai-practice-heading">
            <strong>Выбери испытание · {aiPractices.length}</strong>
            <p>Открой свиток по теме, которую хочешь потренировать.</p>
          </div>
          <div className="ai-practice-tabs" role="group" aria-label="Испытания ИИ-наставника">
            {aiPractices.map((practice, index) => (
              <button
                key={practice.id}
                className={
                  practice.id === selectedAiPracticeId ? "active" : ""
                }
                onClick={() => selectAiPractice(practice)}
                disabled={isAnalyzingSolution}
                aria-pressed={practice.id === selectedAiPracticeId}
              >
                <span>Испытание {index + 1}</span>
                <strong>{practice.title}</strong>
              </button>
            ))}
          </div>

          <div className="ai-lab-workspace">
            <aside className="ai-mission-brief">
              <span className="ai-brief-label">
                {currentAiPractice.topic_title}
              </span>
              <h3>{currentAiPractice.title}</h3>
              <p className="ai-practice-story">{currentAiPractice.story}</p>

              <div className="ai-assignment">
                <span>Королевский заказ</span>
                <p>{currentAiPractice.assignment}</p>
              </div>

              <p className="ai-status-message">
                ИИ может ошибаться: сверяй подсказки с теорией. В этом браузере
                сохраняются черновик и последний разбор выбранного испытания.
                При смене испытания они заменяются новым свитком; перед потерей
                изменённого кода или разбора появится предупреждение.
              </p>
              {!isAiDraftSaved && (
                <p className="ai-feedback-error" role="alert">
                  Браузер не разрешил сохранить свиток. Скопируй код перед
                  обновлением страницы, чтобы не потерять изменения.
                </p>
              )}
            </aside>

            <div className="ai-code-area">
              <div className="ai-code-heading">
                <div>
                  <span>Твой свиток</span>
                  <strong>solution.cs</strong>
                </div>
                <span className="code-language">C#</span>
              </div>

              <label className="visually-hidden" htmlFor="student-solution">
                Решение задания на C#
              </label>
              <textarea
                id="student-solution"
                className="ai-code-editor"
                value={studentSolution}
                onChange={(event) => {
                  if (aiDraft) updateAiDraft({
                    ...aiDraft, studentSolution: event.target.value, feedback: null,
                  });
                  setAiError(null);
                }}
                maxLength={8000}
                spellCheck={false}
                readOnly={isAnalyzingSolution}
                aria-busy={isAnalyzingSolution}
              />

              <label className="ai-cloud-consent">
                <input
                  type="checkbox"
                  checked={cloudReviewConsent}
                  onChange={(event) => setCloudReviewConsent(event.target.checked)}
                  disabled={isAnalyzingSolution}
                />
                <span>
                  Разрешаю отправить условие, эталон и мой код в Groq для разбора.
                  Не вставляй пароли, API-ключи и персональные данные.
                </span>
              </label>

              <div className="ai-code-actions">
                <span>{studentSolution.length} / 8000 символов</span>
                <button
                  className="ai-analyze-button"
                  onClick={analyzeStudentSolution}
                  disabled={
                    !aiStatus?.available ||
                    isCheckingAiStatus ||
                    !cloudReviewConsent ||
                    studentSolution.trim().length < 12 ||
                    isAnalyzingSolution
                  }
                >
                  {isAnalyzingSolution
                    ? "Разбираем решение..."
                    : "Разобрать решение с ИИ"}
                </button>
              </div>
            </div>
          </div>

          {isAnalyzingSolution && (
            <p className="ai-pending-message" role="status">
              Свиток отправлен в Groq. Ждём облачный разбор — обычно это недолго,
              но сервер может отвечать до минуты. Можно продолжить обычные задания.
            </p>
          )}

          {aiFeedback && (
            <article
              className={`ai-feedback-card ${aiFeedback.verdict}`}
              aria-live="polite"
            >
              <div className="ai-feedback-heading">
                <div>
                  <span>Вердикт наставника</span>
                  <h3>{getAiVerdictLabel(aiFeedback.verdict)}</h3>
                </div>
              </div>

              <p className="ai-feedback-summary">{aiFeedback.summary}</p>

              <div className="ai-feedback-columns">
                <FeedbackList
                  title="Что уже хорошо"
                  icon="✓"
                  items={aiFeedback.strengths}
                  tone="positive"
                />
                <FeedbackList
                  title="Что мешает решению"
                  icon="!"
                  items={aiFeedback.issues}
                  tone="negative"
                />
                <FeedbackList
                  title="Куда копать"
                  icon="→"
                  items={aiFeedback.hints}
                  tone="hint"
                />
              </div>

              {aiFeedback.suggested_fragment && (
                <div className="ai-suggested-fragment">
                  <span>Небольшая подсказка в коде</span>
                  <pre tabIndex={0} role="region" aria-label="Подсказка наставника на C#">
                    <code>{aiFeedback.suggested_fragment}</code>
                  </pre>
                </div>
              )}
            </article>
          )}
        </div>
      )}
    </section>
  );
}
