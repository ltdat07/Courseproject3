export default function FeedbackList({
  title,
  icon,
  items,
  tone,
}: {
  title: string;
  icon: string;
  items: string[];
  tone: "positive" | "negative" | "hint";
}) {
  return (
    <section className={`ai-feedback-list ${tone}`}>
      <h4>
        <span aria-hidden="true">{icon}</span>
        {title}
      </h4>
      {items.length > 0 ? (
        <ul>
          {items.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      ) : (
        <p>Наставник ничего не отметил.</p>
      )}
    </section>
  );
}
