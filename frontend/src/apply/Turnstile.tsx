import { useEffect, useRef } from "react";

declare global {
  interface Window {
    turnstile?: {
      render: (el: HTMLElement, opts: Record<string, unknown>) => string;
      remove: (id: string) => void;
      reset: (id: string) => void;
    };
    onloadTurnstileCallback?: () => void;
  }
}

const SCRIPT_SRC = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";

let scriptPromise: Promise<void> | null = null;

function loadScript(): Promise<void> {
  if (scriptPromise) return scriptPromise;
  scriptPromise = new Promise((resolve, reject) => {
    if (window.turnstile) return resolve();
    const el = document.createElement("script");
    el.src = SCRIPT_SRC;
    el.async = true;
    el.onload = () => resolve();
    el.onerror = () => reject(new Error("Turnstile не се зареди"));
    document.head.appendChild(el);
  });
  return scriptPromise;
}

type TurnstileProps = {
  siteKey: string;
  onToken: (token: string) => void;
  onError?: () => void;
};

/**
 * Невидим Turnstile widget. В масовия случай студентът не вижда нищо —
 * появява се предизвикателство само при съмнително поведение.
 *
 * Токенът има давност около 5 минути, затова се взима на стъпка 4,
 * непосредствено преди изпращане, а не при зареждане на формата.
 */
export function Turnstile({ siteKey, onToken, onError }: TurnstileProps) {
  const ref = useRef<HTMLDivElement>(null);
  const widgetId = useRef<string | null>(null);
  const onTokenRef = useRef(onToken);
  onTokenRef.current = onToken;

  useEffect(() => {
    let cancelled = false;

    loadScript()
      .then(() => {
        if (cancelled || !ref.current || !window.turnstile) return;
        widgetId.current = window.turnstile.render(ref.current, {
          sitekey: siteKey,
          size: "flexible",
          appearance: "interaction-only",
          language: "bg",
          callback: (token: string) => onTokenRef.current(token),
          "error-callback": () => onError?.(),
          // Токенът изтича преди студентът да е дочел декларациите — подновяваме го.
          "expired-callback": () => {
            if (widgetId.current && window.turnstile) window.turnstile.reset(widgetId.current);
          },
        });
      })
      .catch(() => onError?.());

    return () => {
      cancelled = true;
      if (widgetId.current && window.turnstile) window.turnstile.remove(widgetId.current);
    };
  }, [siteKey, onError]);

  return <div ref={ref} className="min-h-[1px]" />;
}
