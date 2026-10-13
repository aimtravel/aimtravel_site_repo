import type { ApplicationInput } from "../helpers/applySchema";

/**
 * React работи в camelCase, Django в snake_case. Преобразуването е на едно
 * място и е изрично — нарочно НЕ е автоматично, защото автоматичното
 * прекръстване мълчаливо изпраща и полета, които не искаме да пътуват.
 */
export function toApiPayload(
  values: ApplicationInput,
  turnstileToken: string,
): Record<string, unknown> {
  const payload: Record<string, unknown> = {
    email: values.email,
    first_name: values.firstName,
    middle_name: values.middleName,
    last_name: values.lastName,
    phone: values.phone,
    date_of_birth: values.dateOfBirth,
    egn: values.egn,
    id_card_number: values.idCardNumber,
    place_of_birth: values.placeOfBirth,

    university: values.university,
    major: values.major,
    year_of_study: values.yearOfStudy,

    program_option: values.programOption,
    season: Number(values.season),
    office: values.office,

    accepts_terms: values.acceptsTerms,
    declares_truth: values.declaresTruth,
    accepts_gdpr: values.acceptsGdpr,
  };

  // Only include turnstile_token if it's provided (for testing when disabled)
  if (turnstileToken) {
    payload.turnstile_token = turnstileToken;
  }

  return payload;
}

/** Обратната посока — за черновата, за да може да се възстанови във формата. */
export const FIELD_BY_API_NAME: Record<string, keyof ApplicationInput> = {
  email: "email",
  first_name: "firstName",
  middle_name: "middleName",
  last_name: "lastName",
  phone: "phone",
  date_of_birth: "dateOfBirth",
  egn: "egn",
  id_card_number: "idCardNumber",
  place_of_birth: "placeOfBirth",
  university: "university",
  major: "major",
  year_of_study: "yearOfStudy",
  program_option: "programOption",
  season: "season",
  office: "office",
};

/** DRF връща грешките по API имена; формата ги знае по React имена. */
export function apiFieldToFormField(apiField: string): keyof ApplicationInput | undefined {
  return FIELD_BY_API_NAME[apiField];
}
