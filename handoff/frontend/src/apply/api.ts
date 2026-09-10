/**
 * HTTP слоят към Django. Едно място, което знае за CSRF, за формата на
 * DRF грешките и за това, че бекендът връща i18n ключове, а не текст.
 */

export interface ApplyConfig {
  season: string;
  turnstileSiteKey: string;
  offices: { value: string; label: string; address: string }[];
}

export interface ContractResult {
  applicationId: string;
  contractNumber: string;
  contractPdfUrl: string;
  emailSentTo: string;
}

export interface Suggestion {
  value: string;
  label: string;
  hint?: string;
}

/** Грешки по поле, както ги връща DRF: { "egn": ["errors.egn.checksum"] } */
export class ApiValidationError extends Error {
  constructor(public readonly fieldErrors: Record<string, string[]>,
              public readonly detail?: string) {
    super(detail ?? "validation failed");
    this.name = "ApiValidationError";
  }

  /** Първият ключ за дадено поле, готов за подаване на t(). */
  first(field: string): string | undefined {
    return this.fieldErrors[field]?.[0];
  }
}

export class ApiError extends Error {
  constructor(public readonly status: number, public readonly detail?: string) {
    super(detail ?? `HTTP ${status}`);
    this.name = "ApiError";
  }
}

/** Django записва CSRF токена в бисквитка; SessionAuthentication го изисква. */
function csrfToken(): string {
  const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : "";
}

const BASE = "/api/v1";

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    ...init,
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken(),
      ...init.headers,
    },
  });

  if (response.status === 204) return undefined as T;

  let body: unknown = null;
  try { body = await response.json(); } catch { /* празно тяло при 5xx */ }

  if (response.ok) return body as T;

  if (response.status === 400 && body && typeof body === "object") {
    const record = body as Record<string, unknown>;
    const detail = typeof record.detail === "string" ? record.detail : undefined;
    const fieldErrors: Record<string, string[]> = {};
    for (const [key, value] of Object.entries(record)) {
      if (key === "detail") continue;
      fieldErrors[key] = Array.isArray(value) ? value.map(String) : [String(value)];
    }
    throw new ApiValidationError(fieldErrors, detail);
  }

  if (response.status === 429) throw new ApiError(429, "errors.tooManyRequests");
  throw new ApiError(response.status,
    (body as { detail?: string } | null)?.detail ?? "errors.submitFailed");
}

/* ------------------------------------------------------------------ */

export const api = {
  config: () => request<ApplyConfig>("/apply/config"),

  lookup: (kind: "universities" | "cities" | "majors", q: string, signal?: AbortSignal) =>
    request<Suggestion[]>(`/lookup/${kind}?q=${encodeURIComponent(q)}`, { method: "GET", signal }),

  saveDraft: (draftId: string | null, values: Record<string, unknown>) =>
    request<{ draft_id: string }>("/applications/draft", {
      method: "PUT",
      body: JSON.stringify({ draft_id: draftId, values }),
    }),

  /**
   * Idempotency-Key прави повторното изпращане безопасно: двойно кликване
   * или retry на мрежата връща същия договор вместо да издава втори.
   * Ключът се генерира ВЕДНЪЖ на сесия на формата, не при всеки опит.
   */
  submit: (values: Record<string, unknown>, idempotencyKey: string) =>
    request<ContractResult>("/applications", {
      method: "POST",
      headers: { "Idempotency-Key": idempotencyKey },
      body: JSON.stringify(values),
    }),
};

/** snake_case от Django → camelCase за React, само за отговорите, които четем. */
export function toContractResult(raw: Record<string, string>): ContractResult {
  return {
    applicationId: raw.application_id,
    contractNumber: raw.contract_number,
    contractPdfUrl: raw.contract_pdf_url,
    emailSentTo: raw.email_sent_to,
  };
}
