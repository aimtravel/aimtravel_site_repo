import i18n from "i18next";
import { initReactI18next } from "react-i18next";

import bgCommon from "./locales/bg/common.json";
import bgWat from "./locales/bg/wat.json";
import bgPricing from "./locales/bg/pricing.json";
import bgOffers from "./locales/bg/offers.json";
import bgApply from "./locales/bg/apply.json";
import bgPortal from "./locales/bg/portal.json";
import bgChat from "./locales/bg/chat.json";

export const defaultNS = "common" as const;

export const resources = {
  bg: {
    common: bgCommon,
    wat: bgWat,
    pricing: bgPricing,
    offers: bgOffers,
    apply: bgApply,
    portal: bgPortal,
    chat: bgChat,
  },
  // en: { ... }  ← добави en.json тук, без промени по компонентите
} as const;

i18n.use(initReactI18next).init({
  resources,
  lng: "bg",
  fallbackLng: "bg",
  defaultNS,
  ns: ["common", "wat", "pricing", "offers", "apply", "portal", "chat"],
  interpolation: {
    escapeValue: false, // React вече ескейпва
  },
  returnNull: false,
});

export default i18n;

/* ------------------------------------------------------------------
   Типова безопасност — прави t() автодовършим и хваща счупени ключове
   ------------------------------------------------------------------ */
declare module "i18next" {
  interface CustomTypeOptions {
    defaultNS: typeof defaultNS;
    resources: (typeof resources)["bg"];
    returnNull: false;
  }
}

/* ------------------------------------------------------------------
   Формати — НЕ влизат в JSON, защото зависят от локала
   ------------------------------------------------------------------ */
export const formatCurrencyUsd = (value: number, locale = "bg-BG") =>
  new Intl.NumberFormat(locale, {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);

export const formatCurrencyBgn = (value: number, locale = "bg-BG") =>
  new Intl.NumberFormat(locale, {
    style: "currency",
    currency: "BGN",
    maximumFractionDigits: 0,
  }).format(value);

export const formatDate = (value: Date | string, locale = "bg-BG") =>
  new Intl.DateTimeFormat(locale, {
    day: "numeric",
    month: "long",
    year: "numeric",
  }).format(typeof value === "string" ? new Date(value) : value);

export const formatDateTime = (value: Date | string, locale = "bg-BG") =>
  new Intl.DateTimeFormat(locale, {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(typeof value === "string" ? new Date(value) : value);
