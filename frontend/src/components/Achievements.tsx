import PixelIcon from "./PixelIcon";

type Props = {
  achievements: string[];
};

export default function Achievements({
  achievements,
}: Props) {
  return (
    <section className="achievements-box">
      <div className="section-heading">
        <div>
          <span className="section-kicker achievement-kicker">
            Зал славы
          </span>
          <h2>Достижения героя</h2>
          <p>
            Награды за пройденные главы курса.
          </p>
        </div>

        <div className="achievement-counter">
          <strong>{achievements.length}</strong>
          <span>получено</span>
        </div>
      </div>

      <div className="achievements-list">
        {achievements.map((achievement) => (
          <article className="achievement" key={achievement}>
            <span className="achievement-trophy" aria-hidden="true">
              <PixelIcon name="crown" size={40} />
            </span>
            <div>
              <span>Достижение открыто</span>
              <strong>{achievement}</strong>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
