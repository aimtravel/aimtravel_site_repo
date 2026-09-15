import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { X } from "lucide-react";
import { Button } from "@/components/ui/button";

/* Ключът в localStorage — записва се САМО при „Съгласявам се".
   Отказ и затваряне (X, Escape, клик върху overlay) НЕ записват нищо, така
   че модалът ще се появи отново при следващо посещение. */
const CONSENT_KEY = "aim.cookieConsent";

export function CookieConsent() {
  const { t } = useTranslation("apply");
  const [open, setOpen] = useState(false);

  useEffect(() => {
    try {
      if (localStorage.getItem(CONSENT_KEY) !== "accepted") setOpen(true);
    } catch {
      /* private mode / disabled storage — показваме модала веднъж */
      setOpen(true);
    }
  }, []);

  useEffect(() => {
    if (!open) return;

    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };

    window.addEventListener("keydown", onKey);
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = previousOverflow;
    };
  }, [open]);

  if (!open) return null;

  const decline = () => setOpen(false);
  const accept = () => {
    try {
      localStorage.setItem(CONSENT_KEY, "accepted");
    } catch {
      /* без storage просто затваряме за текущата сесия */
    }
    setOpen(false);
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="cookie-consent-title"
      aria-describedby="cookie-consent-body"
      className="fixed inset-0 z-[100] grid place-items-center bg-navy-900/70 p-4 backdrop-blur-sm"
      onClick={(e) => {
        if (e.target === e.currentTarget) decline();
      }}
    >
      <div className="relative w-full max-w-lg rounded-[18px] border bg-card p-6 shadow-2xl sm:p-7">
        <button
          type="button"
          onClick={decline}
          aria-label={t("cookies.close")}
          className="absolute right-3 top-3 grid h-8 w-8 place-items-center rounded-full text-muted-foreground transition hover:bg-muted hover:text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
          <X className="h-4 w-4" />
        </button>

        <h2
          id="cookie-consent-title"
          className="mb-3 pr-8 font-display text-lg font-bold uppercase tracking-tight text-secondary sm:text-xl"
        >
          {t("cookies.title")}
        </h2>

        <p id="cookie-consent-body" className="text-sm leading-relaxed text-muted-foreground">
          {t("cookies.body")}
        </p>

        <ul className="mt-3 grid list-disc gap-1 pl-5 text-[13px] text-muted-foreground">
          {(t("cookies.items", { returnObjects: true }) as string[]).map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>

        <p className="mt-4 text-xs italic text-muted-foreground">{t("cookies.note")}</p>

        <div className="mt-6 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <Button type="button" variant="outline" onClick={decline}>
            {t("cookies.decline")}
          </Button>
          <Button type="button" onClick={accept} autoFocus>
            {t("cookies.accept")}
          </Button>
        </div>
      </div>
    </div>
  );
}
