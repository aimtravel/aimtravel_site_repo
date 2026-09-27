import { useCallback } from "react";
import { useTranslation } from "react-i18next";
import type { Namespace } from "i18next";

/* ------------------------------------------------------------------
   Преводи на грешки, чиито ключове идват по време на изпълнение —
   zod съобщения ("apply:errors.egn.checksum"), DRF отговори
   ("errors.egn.checksum"), ApiError.detail. Типизираният t() не може
   да ги провери статично, затова кастът е събран тук, на едно място,
   вместо `as any` по компонентите.
   ------------------------------------------------------------------ */

const ERROR_FALLBACKP_KEY = "common:errors.generic";

/**
 * Връща функция, която превежда ключ за грешка от runtime източник.
 * Непознат ключ → общото съобщение за грешка, никога суров ключ в UI.
 * @params nameSpace - Името на namespace-а за преводите (по подразбиране "common").
 * @returns Функция, която приема ключ за грешка и връща превода му или общото съобщение за грешка, ако ключът не съществува.
 */
export function useErrorMessage(nameSpace: Namespace = "common") {
  const { t, i18n } = useTranslation(nameSpace);
  const translate = t as unknown as (key: string | string[]) => string;

  return useCallback(
    (key?: string | null, fallback: string = ERROR_FALLBACKP_KEY): string => {
      if (!key) return translate(fallback);
      return i18n.exists(key, { ns: nameSpace }) ? translate(key) : translate(fallback);
    },
    [translate, i18n, nameSpace],
  );
}
