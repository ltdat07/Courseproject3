import CodePanel from "./CodePanel";

const THEORY_SECTION_TITLES = new Set([
  "Суть",
  "Основные конструкции",
  "Работа со строками",
  "Консольный обмен",
  "Преобразование ввода",
  "Перечисления",
  "Структуры",
  "Работа с файлами",
  "JSON",
  "Интерфейсы",
  "Обобщения",
  "Пример",
  "Частые ошибки",
  "Что запомнить",
]);

export default function TheoryContent({ theory }: { theory?: string }) {
  if (!theory) {
    return <p>Этот свиток пока восстанавливают архивариусы.</p>;
  }

  return (
    <div className="theory-content">
      {theory.split("```").map((block, blockIndex) => {
        if (blockIndex % 2 === 1) {
          const code = block.replace(/^csharp\s*\n?/, "").trim();

          return (
            <CodePanel
              key={`code-${blockIndex}`}
              className="theory-code-panel"
              title="Пример из свитка"
              code={code}
            />
          );
        }

        const paragraphs = block
          .trim()
          .split(/\n{2,}/)
          .map((paragraph) => paragraph.trim())
          .filter(Boolean);

        if (paragraphs.length === 0) {
          return null;
        }

        return (
          <div className="theory-copy" key={`copy-${blockIndex}`}>
            {paragraphs.map((paragraph, paragraphIndex) =>
              THEORY_SECTION_TITLES.has(paragraph) ? (
                <h4 key={`${blockIndex}-${paragraphIndex}`}>{paragraph}</h4>
              ) : (
                <p key={`${blockIndex}-${paragraphIndex}`}>{paragraph}</p>
              ),
            )}
          </div>
        );
      })}
    </div>
  );
}
