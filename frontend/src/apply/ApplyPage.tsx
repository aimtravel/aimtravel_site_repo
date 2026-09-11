import * as React from "react";
import { useTranslation } from "react-i18next";
import { api, type ApplyConfig } from "./api";
import { ApplyWizard } from "./ApplyWizard";

interface Bootstrap {
  season?: string;
  turnstileSiteKey?: string;
  offices?: ApplyConfig["offices"];
}

/**
 * Обвивката около wizard-а: hero секцията, страничната колона и зареждането
 * на конфигурацията.
 *
 * Сезонът и Turnstile ключът НЕ са в bundle-а: сезонът се сменя на 1 юни, а
 * ключът може да бъде ротиран — и двете без rebuild. Django ги подава като
 * data-bootstrap атрибут (нула допълнителни заявки), а fetch-ът е резервен
 * вариант, ако template-ът не ги е сложил.
 */
export function ApplyPage({ bootstrap }: { bootstrap: Bootstrap }) {
  const { t } = useTranslation("apply");
  const [config, setConfig] = React.useState<ApplyConfig | null>(
    bootstrap.season && bootstrap.turnstileSiteKey
      ? {
          season: bootstrap.season,
          turnstileSiteKey: bootstrap.turnstileSiteKey,
          offices: bootstrap.offices ?? [],
        }
      : null,
  );
  const [failed, setFailed] = React.useState(false);

  React.useEffect(() => {
    if (config) return;
    api
      .config()
      .then((raw) =>
        setConfig({
          season: String((raw as unknown as Record<string, unknown>).season),
          turnstileSiteKey: (raw as unknown as Record<string, string>).turnstile_site_key,
          offices: raw.offices,
        }),
      )
      .catch(() => setFailed(true));
  }, [config]);

  return (
    <>
      <header className="relative overflow-hidden bg-gradient-to-b from-navy-800 to-navy-900 pb-24 pt-11 text-white">
        <div
          aria-hidden
          className="absolute -right-10 top-0 bottom-0 w-56 opacity-[0.14]
                     [background:repeating-linear-gradient(105deg,#E8635C_0_14px,transparent_14px_34px)]"
        />
        <div className="container">
          <p className="mb-2.5 font-mono text-xs uppercase tracking-[0.16em] text-coral">
            {t("eyebrow", { season: config?.season ?? "" })}
          </p>
          <h1 className="text-[34px] uppercase text-white">{t("title")}</h1>
          <p className="mt-2.5 max-w-[620px] text-[#B9C6D4]">
            {t("subtitle")} <b className="text-white">{t("noPaymentNote")}</b>
          </p>
        </div>
        {/* Куполът е бранд мотив от съществуващия сайт. */}
        <div
          aria-hidden
          className="absolute -bottom-14 -left-[5%] -right-[5%] h-28 rounded-t-[50%] bg-muted"
        />
      </header>

      <main className="relative z-10 -mt-13 pb-16">
        <div className="container grid items-start gap-6 lg:grid-cols-[1fr_316px]">
          {failed ? (
            <div role="alert" className="rounded-[18px] border bg-card p-8 text-center">
              <p className="font-semibold">{t("errors.configFailed")}</p>
            </div>
          ) : config ? (
            <ApplyWizard config={config} />
          ) : (
            <div className="h-[520px] animate-pulse rounded-[18px] border bg-card" />
          )}

          <aside className="grid gap-4">
            <SideCard
              title={t("aside.requirements")}
              items={t("aside.requirementItems", { returnObjects: true }) as string[]}
            />
            <SideCard
              dark
              title={t("aside.whyTitle")}
              items={t("aside.whyItems", { returnObjects: true }) as string[]}
            />
          </aside>
        </div>
      </main>
    </>
  );
}

function SideCard({ title, items, dark }: { title: string; items: string[]; dark?: boolean }) {
  return (
    <section
      className={
        dark
          ? "rounded-[18px] bg-navy-800 p-5 text-[#C9D3DE]"
          : "rounded-[18px] border bg-card p-5 shadow-sm"
      }
    >
      <h3 className={`mb-3 text-[13px] uppercase tracking-wider ${dark ? "text-coral" : ""}`}>
        {title}
      </h3>
      <ul className="grid list-disc gap-1.5 pl-4 text-[13.5px]">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </section>
  );
}
