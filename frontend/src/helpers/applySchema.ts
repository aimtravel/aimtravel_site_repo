import { z } from "zod";

/* ---------------------------------------------------------------
   Единственият източник на истина за валидацията във фронтенда.
   Огледален на api/schemas.py (Pydantic) — при промяна се пипат двата.
   --------------------------------------------------------------- */

const EGN_WEIGHTS = [2, 4, 8, 5, 10, 9, 7, 3, 6];

/** Контролна цифра на ЕГН по БДС. */
export function isValidEgn(egn: string): boolean {
  if (!/^\d{10}$/.test(egn)) return false;
  const sum = EGN_WEIGHTS.reduce((a, w, i) => a + w * Number(egn[i]), 0);
  return (sum % 11) % 10 === Number(egn[9]);
}

/** Дата на раждане, извлечена от ЕГН — служи за кръстосана проверка. */
export function dobFromEgn(egn: string): string | null {
  if (!/^\d{10}$/.test(egn)) return null;
  let year = Number(egn.slice(0, 2));
  let month = Number(egn.slice(2, 4));
  const day = Number(egn.slice(4, 6));
  if (month > 40) {
    month -= 40;
    year += 2000;
  } else if (month > 20) {
    month -= 20;
    year += 1800;
  } else year += 1900;
  if (month < 1 || month > 12 || day < 1 || day > 31) return null;
  return `${year}-${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
}

/** Възраст към дадена дата (стартът на програмата, не „днес“). */
export function ageAt(isoDob: string, at: Date): number {
  const [y, m, d] = isoDob.split("-").map(Number);
  let age = at.getFullYear() - y;
  const delta = at.getMonth() + 1 - m || at.getDate() - d;
  if (delta < 0) age -= 1;
  return age;
}

/** Стартът на сезона — възрастовият критерий се мери спрямо него, не спрямо днес. */
export const seasonStart = (season: string) => new Date(Number(season), 5, 1);

/**
 * Записваме винаги за ПРЕДСТОЯЩОТО лято — никога за години напред.
 * След 1 юни текущата лятна кампания е приключила, значи следващата е догодина.
 * Есен 2026 → лято 2027. Март 2027 → пак лято 2027.
 * ВНИМАНИЕ: авторитетът е бекендът (GET /api/v1/apply/config). Тази функция
 * е само за офлайн тестове и за фолбек — браузърният часовник не е надежден.
 */
export function upcomingSeason(today = new Date()): string {
  const year = today.getFullYear();
  return String(today.getMonth() >= 5 ? year + 1 : year);
}

const cyrillic = (field: string) => z.string().trim().min(2, `apply:errors.${field}.short`)
  .max(30).regex(/^[А-Яа-яЍѝ]+(?:[ -][А-Яа-яЍѝ]+)*$/, `apply:errors.${field}.cyrillic`);

export const step1Schema = z.object({
  email: z.string().trim().toLowerCase().email("apply:errors.email.invalid"),
  firstName: cyrillic("firstName"), middleName: cyrillic("middleName"), lastName: cyrillic("lastName"),
  phone: z.string().trim().transform(v => v.replace(/[^\d+]/g, ""))
    .refine(v => /^\+359[789]\d{8}$/.test(v), "apply:errors.phone.invalid"),
  egn: z.string().trim().refine(isValidEgn, "apply:errors.egn.checksum"),
  idCardNumber: z.string().trim().regex(/^\d{9}$/, "apply:errors.idCard.invalid"),
});
export const step2Schema = z.object({
  programOption: z.enum(["full_arranged", "self_arranged"]),
  season: z.string().regex(/^\d{4}$/),
  saveExchange: z.boolean(),
  discountCode: z.string().trim().max(32),
});
export const step3Schema = z.object({
  acceptsTerms: z.literal(true, {errorMap: () => ({message: "apply:errors.consent.terms"})}),
  declaresTruth: z.literal(true, {errorMap: () => ({message: "apply:errors.consent.truth"})}),
  acceptsGdpr: z.literal(true, {errorMap: () => ({message: "apply:errors.consent.gdpr"})}),
});
export const applicationSchema = step1Schema.merge(step2Schema).merge(step3Schema);
export type ApplicationInput = z.infer<typeof applicationSchema>;
export const STEP_SCHEMAS = [step1Schema, step2Schema, step3Schema] as const;
export const STEP_FIELDS: readonly (keyof ApplicationInput)[][] = [
  ["email", "firstName", "middleName", "lastName", "phone", "egn", "idCardNumber"],
  ["programOption", "season", "saveExchange", "discountCode"],
  ["acceptsTerms", "declaresTruth", "acceptsGdpr"],
];
