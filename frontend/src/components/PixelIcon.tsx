export type PixelIconName =
  | "tower"
  | "scroll"
  | "sword"
  | "gem"
  | "book"
  | "key"
  | "flask"
  | "chest"
  | "shield"
  | "crown"
  | "lock"
  | "arrow";

type Props = {
  name: PixelIconName;
  size?: number;
  className?: string;
};

const light = "#e3c685";
const shadow = "#795431";
const ink = "#302219";

const artwork: Record<PixelIconName, readonly (readonly [string, string])[]> = {
  tower: [
    ["M3 2h5v4h2V2h4v4h2V2h5v9h-2v9h2v3H3v-3h2v-9H3Z", ink],
    ["M4 3h3v4h4V3h2v4h4V3h3v7h-2v11h2v1H4v-1h2V10H4Z", "currentColor"],
    ["M4 3h3v1H5v4H4Zm7 0h2v1h-2Zm6 0h3v1h-3ZM4 8h16v1H4Zm2 3h2v10H6Z", light],
    ["M17 11h1v10h-1ZM4 21h16v1H4Z", shadow],
    ["M11 12h2v3h-2Zm-1 5h4v1h1v4H9v-4h1Z", ink],
    ["M10 19h1v3h-1Z", shadow],
  ],
  scroll: [
    ["M6 2h13v2h2v5h-3v10h-2v3H3v-2H1v-5h4V4h1Z", ink],
    ["M7 3h11v1h2v4h-3V6H7Zm-1 3h10v13h-2v2H4v-1H2v-4h4Z", "currentColor"],
    ["M7 3h11v1H8v2H7ZM6 6h2v11H6ZM3 17h2v2H3Z", light],
    ["M16 6h1v13h-2v2H4v-1h10v-2h2Z", shadow],
    ["M9 8h5v1H9Zm0 3h5v1H9Zm0 3h4v1H9Z", ink],
  ],
  sword: [
    ["M17 1h6v6h-2v2h-2v2h-2v2h-2v2h2v2h2v2h-4v-2h-2v2h-2v2H9v2H5v-2H3v-4h2v-2h2v-2H5v-2H3V7h2v2h2v2h2v-2h2V7h2V5h2V3h2Z", ink],
    ["M18 2h4v4h-2v2h-2v2h-2v2h-2v2h-3v-3h1V8h2V6h2V4h2Z", "currentColor"],
    ["M18 2h4v1h-3v2h-2v2h-2v2h-2v2h-2v-1h1V8h2V6h2V4h2Z", light],
    ["M20 5h2v1h-2v2h-2v2h-2v2h-2v2h-2v-1h1v-2h2V9h2V7h3Z", shadow],
    ["M4 8h1v2h2v2h2v2h2v2h2v2h3v-1h-2v-2h-2v-2h-2v-2H8V9H6V8Z", "currentColor"],
    ["M8 15h2v2H8v2H6v2H4v-3h2v-2h2Z", shadow],
    ["M5 20h2v2H5Z", light],
  ],
  gem: [
    ["M7 2h10v2h3v3h2v7h-2v3h-3v3h-3v2h-4v-2H7v-3H4v-3H2V7h2V4h3Z", ink],
    ["M8 3h8v2h3v3h2v5h-2v3h-3v3h-3v2h-2v-2H8v-3H5v-3H3V8h2V5h3Z", "currentColor"],
    ["M8 3h8v2H9v3H6v4H3V8h2V5h3Z", light],
    ["M16 5h3v3h2v5h-2v3h-3v3h-3v2h-1v-8h2V8h2Z", shadow],
    ["M10 6h3v2h2v4h-2v4h-2v-4H9V8h1Z", light],
  ],
  book: [
    ["M2 4h8v1h4V4h8v16h-8v1h-4v-1H2Z", ink],
    ["M3 5h6v1h2v13H9v-1H3Zm12 0h6v13h-6v1h-2V6h2Z", "currentColor"],
    ["M3 5h6v1h2v1H8V6H4v10H3Zm12 0h6v1h-6v1h-2V6h2Z", light],
    ["M3 17h6v1h2v1H9v-1H3Zm17-11h1v12h-6v1h-2v-1h2v-1h5Z", shadow],
    ["M5 8h3v1H5Zm0 3h4v1H5Zm0 3h4v1H5Zm10-6h4v1h-4Zm0 3h4v1h-4Zm0 3h3v1h-3Z", ink],
  ],
  key: [
    ["M5 2h8v2h2v2h2v7h-2v2h-2v2h-2v2H9v3H2v-5h2v-2h2v-2H4v-2H2V5h3Z", ink],
    ["M6 3h6v2h2v2h2v5h-2v2h-3v2H9v2H7v3H3v-3h2v-2h2v-3H5v-2H3V6h3Z", "currentColor"],
    ["M6 3h6v1H7v2H5v4H4V6h2ZM3 18h2v1H4v2H3Z", light],
    ["M14 8h2v4h-2v2h-3v2H9v2H7v3H5v-2h1v-2h2v-2h2v-2h3v-2h1Z", shadow],
    ["M8 6h3v1h1v4H8v-1H7V7h1Z", ink],
  ],
  flask: [
    ["M7 1h10v4h-2v5h2v2h2v2h2v7h-2v2H5v-2H3v-7h2v-2h2v-2h2V5H7Z", ink],
    ["M8 2h8v2h-2v7h2v2h2v2h2v5h-2v2H6v-2H4v-5h2v-2h2v-2h2V4H8Z", "currentColor"],
    ["M8 2h8v1h-6v1H9Zm2 3h1v7H9v2H7v2H5v4H4v-5h2v-2h2v-2h2Z", light],
    ["M7 15h10v1h2v4h-2v1H7v-1H5v-4h2Z", shadow],
    ["M7 16h3v2H7Zm6 2h2v2h-2Zm-1-5h2v2h-2Z", light],
  ],
  chest: [
    ["M5 3h14v2h3v16H2V5h3Z", ink],
    ["M6 4h12v2h3v5H3V6h3ZM3 13h18v7H3Z", "currentColor"],
    ["M6 4h12v1H6Zm-3 2h3v5H3Zm0 7h2v6H3Z", light],
    ["M18 6h3v5h-3Zm0 7h3v7H3v-1h15Z", shadow],
    ["M7 6h1v5H7Zm9 0h1v5h-1ZM7 13h1v6H7Zm9 0h1v6h-1Zm-6-3h4v6h-4Z", ink],
    ["M11 11h2v3h-2Z", light],
  ],
  shield: [
    ["M11 1h2v2h4v2h5v10h-2v3h-3v3h-3v2h-4v-2H7v-3H4v-3H2V5h5V3h4Z", ink],
    ["M11 3h2v2h4v1h4v8h-2v3h-3v3h-3v2h-2v-2H8v-3H5v-3H3V6h4V5h4Z", "currentColor"],
    ["M11 3h2v2h-2v1H7v1H4v7H3V6h4V5h4Z", light],
    ["M18 7h3v7h-2v3h-3v3h-3v2h-1v-3h3v-3h3v-3Z", shadow],
    ["M11 7h2v4h4v2h-4v5h-2v-5H7v-2h4Z", ink],
  ],
  crown: [
    ["M10 2h4v4h2v3h2V6h5v8h-2v7H3v-7H1V6h5v3h2V6h2Z", ink],
    ["M11 3h2v4h2v3h4V7h3v6h-2v7H4v-7H2V7h3v3h4V7h2Z", "currentColor"],
    ["M11 3h2v1h-1v4h-2v3H8v-1h1V7h2ZM2 7h3v1H3v5h1v4H3v-4H2Zm17 0h3v1h-3ZM4 18h16v1H4Z", light],
    ["M19 10h3v3h-2v7H4v-1h15Z", shadow],
    ["M11 12h2v3h-2ZM6 14h2v2H6Zm10 0h2v2h-2Z", ink],
  ],
  lock: [
    ["M8 2h8v2h2v6h3v12H3V10h3V4h2Z", ink],
    ["M8 3h8v2h1v6h-3V6h-4v5H7V5h1ZM4 11h16v10H4Z", "currentColor"],
    ["M8 3h8v1H9v2H8v5H7V5h1ZM4 11h16v1H5v8H4Z", light],
    ["M18 12h2v9H4v-1h14Z", shadow],
    ["M10 14h4v3h-1v2h-2v-2h-1Z", ink],
  ],
  arrow: [
    ["M13 4h3v3h3v3h3v4h-3v3h-3v3h-3v-6H2v-4h11Z", ink],
    ["M14 5h1v3h3v3h3v2h-3v3h-3v3h-1v-6H3v-2h11Z", "currentColor"],
    ["M14 5h1v3h3v1h-3v3H3v-1h11Z", light],
  ],
};

export default function PixelIcon({ name, size = 32, className }: Props) {
  return (
    <svg
      className={className ? `pixel-icon ${className}` : "pixel-icon"}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      shapeRendering="crispEdges"
      aria-hidden="true"
      focusable="false"
    >
      {artwork[name].map(([d, fill], index) => (
        <path key={index} d={d} fill={fill} />
      ))}
    </svg>
  );
}
