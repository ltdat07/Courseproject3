type Props = {
  title: string;
  code: string;
  className?: string;
};

export default function CodePanel({ title, code, className }: Props) {
  return (
    <div className={className ? `code-panel ${className}` : "code-panel"}>
      <div className="code-panel-header">
        <span>{title}</span>
        <span className="code-language">C#</span>
      </div>
      <pre className="code-block">
        <code>{code}</code>
      </pre>
    </div>
  );
}
