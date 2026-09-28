import { useCallback } from "react";
import { apiFetch } from "./api";
import type { CurrentUser } from "./types";
import HeroSummary from "./components/HeroSummary";
import Achievements from "./components/Achievements";
import AnalyticsPanel from "./components/AnalyticsPanel";
import TopicCatalog from "./components/TopicCatalog";
import AiMentor from "./components/AiMentor";
import LessonView from "./components/LessonView";
import PixelIcon from "./components/PixelIcon";
import useCourse from "./hooks/useCourse";
import useAnalytics from "./hooks/useAnalytics";
import useAiMentor from "./hooks/useAiMentor";
import "./App.css";

type Props = {
  user: CurrentUser;
  onLogout: () => void;
  isLoggingOut: boolean;
};

function App({ user, onLogout, isLoggingOut }: Props) {
  const request = useCallback(
    (url: string, options?: RequestInit) => apiFetch(url, options, user.id),
    [user.id],
  );
  const {
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
  } = useCourse(request);
  const {
    analytics,
    isLoadingAnalytics,
    analyticsError,
    attemptedTopicAnalytics,
    weakTopicAnalytics,
  } = useAnalytics(request, answerRevision);
  // Состояние наставника сохраняется при переходе к уроку.
  const {
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
  } = useAiMentor(request, user.id);

  return (
    <main className="app">
      <header className="account-bar">
        <div className="account-identity">
          <span className="account-avatar" aria-hidden="true"><PixelIcon name="shield" /></span>
          <div><small>Личный профиль · @{user.username}</small><strong>{user.display_name || user.username}</strong></div>
        </div>
        <button onClick={onLogout} disabled={isLoggingOut || isAnalyzingSolution || isCheckingAnswer}>
          {isLoggingOut ? "Выходим…" : "Выйти"}
        </button>
      </header>
      <HeroSummary totalXp={totalXp} achievements={achievements}
        completedTopicIds={completedTopicIds} learningProgress={learningProgress}
        isLoadingTopics={isLoadingTopics} topics={topics}
        isCourseCompleted={isCourseCompleted} nextLevelNumber={nextLevelNumber} />

      {courseError && (
        <div className="result error">
          <strong>Ошибка</strong>
          <p>{courseError}</p>
        </div>
      )}

      {!selectedTopic && (
        <>
          {achievements.length > 0 && <Achievements achievements={achievements} />}

          <AnalyticsPanel analytics={analytics} isLoadingAnalytics={isLoadingAnalytics}
            analyticsError={analyticsError} weakTopicAnalytics={weakTopicAnalytics}
            attemptedTopicAnalytics={attemptedTopicAnalytics} />

          <TopicCatalog topics={topics} completedTopicIds={completedTopicIds}
            unlockedTopicIds={unlockedTopicIds} isLoadingTopics={isLoadingTopics}
            loadingTopicId={loadingTopicId} openTopic={openTopic} />

          <AiMentor aiStatus={aiStatus} isCheckingAiStatus={isCheckingAiStatus}
            refreshAiConnection={refreshAiConnection} isAnalyzingSolution={isAnalyzingSolution}
            setIsAiLabOpen={setIsAiLabOpen} aiPractices={aiPractices} isAiLabOpen={isAiLabOpen}
            aiError={aiError} currentAiPractice={currentAiPractice}
            selectedAiPracticeId={selectedAiPracticeId} selectAiPractice={selectAiPractice}
            isAiDraftSaved={isAiDraftSaved} studentSolution={studentSolution}
            aiDraft={aiDraft} updateAiDraft={updateAiDraft} setAiError={setAiError}
            cloudReviewConsent={cloudReviewConsent} setCloudReviewConsent={setCloudReviewConsent}
            analyzeStudentSolution={analyzeStudentSolution} aiFeedback={aiFeedback} />
        </>
      )}

      {selectedTopic && (
        <LessonView selectedTopic={selectedTopic} currentTask={currentTask}
          goBackToTopics={goBackToTopics} currentTaskIndex={currentTaskIndex} tasks={tasks}
          selectedOptionId={selectedOptionId} setSelectedOptionId={setSelectedOptionId}
          answerResult={answerResult} checkAnswer={checkAnswer} isCheckingAnswer={isCheckingAnswer}
          retryTask={retryTask} isLastTask={isLastTask} goToNextTask={goToNextTask} />
      )}
    </main>
  );
}

export default App;
