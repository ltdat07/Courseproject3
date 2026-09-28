import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import App from "./App";
import PixelIcon from "./components/PixelIcon";
import { API_BASE_URL, apiFetch } from "./api";
import type { CurrentUser } from "./types";
import "./AccountApp.css";

export default function AccountApp() {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [mode, setMode] = useState<"login" | "register">("login");
  const [error, setError] = useState<{ message: string; connection?: boolean } | null>(null);
  const [busy, setBusy] = useState(false);
  const [retry, setRetry] = useState(0);

  useEffect(() => {
    let cancelled = false;
    const expired = () => { setUser(null); setError({ message: "Войди в аккаунт, чтобы продолжить." }); };
    window.addEventListener("trainer:unauthorized", expired);
    apiFetch(`${API_BASE_URL}/users/me`)
      .then(async (response) => {
        if (response.status === 401) return null;
        if (!response.ok) throw new Error("Не удалось загрузить аккаунт.");
        return response.json() as Promise<CurrentUser>;
      })
      .then((account) => { if (!cancelled) { setUser(account); setError(null); } })
      .catch(() => { if (!cancelled) setError({ message: "Не удалось связаться с сервером. Попробуй ещё раз.", connection: true }); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; window.removeEventListener("trainer:unauthorized", expired); };
  }, [retry]);

  async function authenticate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy) return;
    const form = event.currentTarget;
    const data = new FormData(form);
    const password = String(data.get("password"));
    if (mode === "register" && password !== data.get("confirmation")) {
      setError({ message: "Пароли не совпадают." });
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const response = await apiFetch(`${API_BASE_URL}/auth/${mode}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: String(data.get("username")), password,
          ...(mode === "register" ? { display_name: String(data.get("display_name")) } : {}),
        }),
      });
      if (response.status >= 500) {
        setError({ message: "Сервер временно недоступен. Попробуй ещё раз.", connection: true });
        return;
      }
      const result = await response.json();
      if (!response.ok) throw new Error(typeof result.detail === "string" ? result.detail : "Проверь логин, имя и длину пароля.");
      form.reset();
      setUser(result);
    } catch (err) {
      const connection = err instanceof TypeError || (err instanceof Error && err.name === "TimeoutError");
      setError({
        message: connection ? "Сервер не ответил. Попробуй ещё раз." : err instanceof Error ? err.message : "Не удалось войти.",
        connection,
      });
    } finally {
      setBusy(false);
    }
  }

  async function logout() {
    if (busy) return;
    setBusy(true);
    setError(null);
    try {
      const response = await apiFetch(`${API_BASE_URL}/auth/logout`, { method: "POST" });
      if (!response.ok) throw new Error("Не удалось завершить сессию. Проверь связь и повтори выход.");
      setUser(null);
    } catch (err) {
      setError({ message: err instanceof Error ? err.message : "Не удалось выйти." });
    } finally {
      setBusy(false);
    }
  }

  if (loading) return <main className="account-page"><p role="status">Страж проверяет пропуск…</p></main>;
  if (user) return <>
    {error && <p className="account-notice" role="alert">{error.message}</p>}
    <App key={user.id} user={user} onLogout={logout} isLoggingOut={busy} />
  </>;

  return (
    <main className="account-page">
      <div className="account-emblem" aria-hidden="true"><PixelIcon name="tower" /></div>
      <span className="account-kicker">Королевская академия кода</span>
      <h1>Интерактивный тренажер C#</h1>
      <p className="account-intro">У каждого героя — свой путь. Войди, чтобы сохранить баллы, достижения и историю приключений.</p>
      <div className="account-modes" role="group" aria-label="Вход или регистрация">
        <button aria-pressed={mode === "login"} disabled={busy} onClick={() => { setMode("login"); setError(null); }}>Войти</button>
        <button aria-pressed={mode === "register"} disabled={busy} onClick={() => { setMode("register"); setError(null); }}>Создать аккаунт</button>
      </div>
      <form key={mode} onSubmit={authenticate} className="account-form">
        <label>Логин
          <input name="username" autoComplete="username" required minLength={3} maxLength={30}
            pattern="[A-Za-z0-9_]+" aria-describedby="username-help" disabled={busy} />
        </label>
        <small id="username-help">3–30 латинских букв, цифр или _. Регистр не важен.</small>
        {mode === "register" && <label>Имя героя
          <input name="display_name" autoComplete="nickname" required maxLength={60} disabled={busy} />
        </label>}
        <label>Пароль
          <input type="password" name="password" autoComplete={mode === "login" ? "current-password" : "new-password"}
            required minLength={12} maxLength={128} aria-describedby="password-help" disabled={busy} />
        </label>
        <small id="password-help">12–128 символов. Можно использовать длинную фразу.</small>
        {mode === "register" && <label>Повтори пароль
          <input type="password" name="confirmation" autoComplete="new-password" required minLength={12} maxLength={128} disabled={busy} />
        </label>}
        {error && <p className="account-error" role="alert">{error.message}</p>}
        <button className="account-submit" disabled={busy} type="submit">
          {busy ? "Страж сверяет записи…" : mode === "login" ? "Войти в Академию" : "Начать своё приключение"}
        </button>
      </form>
      {error?.connection && <button className="account-retry" disabled={busy} onClick={() => { setLoading(true); setRetry((n) => n + 1); }}>Проверить связь</button>}
    </main>
  );
}
