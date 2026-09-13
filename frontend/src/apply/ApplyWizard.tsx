import { useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { Controller, FormProvider, useForm, useFormContext } from "react-hook-form";
import { useTranslation } from "react-i18next";
import { zodResolver } from "@hookform/resolvers/zod";
import { Check, Loader2, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";
import { api, ApiError, ApiValidationError, type ApplyConfig, type ContractResult } from "./api";
import { applicationSchema, STEP_FIELDS, type ApplicationInput } from "./applySchema";
import { AutocompleteField } from "./AutocompleteField";
import { ContractIssued } from "./ContractIssued";
import { DateOfBirthPicker } from "./DateOfBirthPicker";
import { useDebouncedCallback } from "./hooks";
import { apiFieldToFormField, toApiPayload } from "./payload";
import { Turnstile } from "./Turnstile";

const DRAFT_KEY = "aim.apply.draftId";
const TIMEOUT_SAVE_DRAFT = 1200;

const STEP_KEYS = ["personal", "education", "program", "contract"] as const;

export function ApplyWizard({ config }: { config: ApplyConfig }) {
  const { t } = useTranslation("apply");
  const [step, setStep] = useState(0);
  const [result, setResult] = useState<ContractResult | null>(null);
  const [savedAt, setSavedAt] = useState<Date | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [turnstileToken, setTurnstileToken] = useState("");

  /* Един ключ за целия живот на формата: retry след таймаут връща същия
     договор вместо да издава втори. Нов ключ има само нова форма. */
  const idempotencyKey = useMemo(() => crypto.randomUUID(), []);
  const draftId = useRef<string | null>(localStorage.getItem(DRAFT_KEY));

  const form = useForm<ApplicationInput>({
    resolver: zodResolver(applicationSchema),
    mode: "onTouched", // не крещим, докато полето още се попълва
    reValidateMode: "onChange",
    defaultValues: {
      email: "",
      firstName: "",
      middleName: "",
      lastName: "",
      phone: "+359",
      dateOfBirth: "",
      egn: "",
      idCardNumber: "",
      placeOfBirth: "",
      university: "",
      major: "",
      yearOfStudy: undefined as never,
      programOption: "full_arranged",
      season: config.season,
      office: "varna",
      acceptsTerms: false as never,
      declaresTruth: false as never,
      acceptsGdpr: false as never,
    },
  });

  /* Автозапис на чернова — 1.2 s след последната промяна, не при всяка клавиша. */
  const saveDraft = useDebouncedCallback((values: Partial<ApplicationInput>) => {
    api
      .saveDraft(draftId.current, values as Record<string, unknown>)
      .then(({ draft_id }) => {
        draftId.current = draft_id;
        localStorage.setItem(DRAFT_KEY, draft_id);
        setSavedAt(new Date());
      })
      // Черновата е удобство, не задължение: ако не се запише, потребителят
      // не бива да вижда грешка по средата на попълването.
      .catch(() => void 0);
  }, TIMEOUT_SAVE_DRAFT);

  useEffect(() => {
    const sub = form.watch((values) => saveDraft(values as Partial<ApplicationInput>));
    return () => sub.unsubscribe();
  }, [form, saveDraft]);

  const next = async () => {
    const ok = await form.trigger(STEP_FIELDS[step] as never, { shouldFocus: true });
    if (ok) {
      setStep((s) => Math.min(3, s + 1));
      window.scrollTo({ top: 180, behavior: "smooth" });
    }
  };
  const back = () => setStep((s) => Math.max(0, s - 1));

  const onSubmit = form.handleSubmit(
    async (values) => {
      setSubmitError(null);
      try {
        const raw = await api.submit(toApiPayload(values, turnstileToken), idempotencyKey);
        localStorage.removeItem(DRAFT_KEY);
        setResult({
          applicationId: (raw as never as Record<string, string>).application_id,
          contractNumber: (raw as never as Record<string, string>).contract_number,
          contractPdfUrl: (raw as never as Record<string, string>).contract_pdf_url,
          emailSentTo: (raw as never as Record<string, string>).email_sent_to,
        });
      } catch (error) {
        if (error instanceof ApiValidationError) {
          /* Бекендът валидира повторно и може да види неща, които фронтендът
             не може — застоял сезон, изтекъл Turnstile токен. Връщаме грешките
             върху конкретните полета и подкарваме потребителя към стъпката им. */
          let firstStep: number | null = null;
          for (const [apiField, messages] of Object.entries(error.fieldErrors)) {
            const field = apiFieldToFormField(apiField);
            if (!field) continue;
            form.setError(field, { message: messages[0] });
            const stepIndex = STEP_FIELDS.findIndex((fields) => fields.includes(field));
            if (stepIndex >= 0 && (firstStep === null || stepIndex < firstStep))
              firstStep = stepIndex;
          }
          if (firstStep !== null) setStep(firstStep);
          setSubmitError(t(error.detail ?? ("errors.fixFieldsBelow" as any)));
        } else if (error instanceof ApiError && error.status === 429) {
          setSubmitError(t("errors.tooManyRequests"));
        } else {
          setSubmitError(t("errors.submitFailed"));
        }
        // Токенът е за еднократна употреба — при повторен опит трябва нов.
        setTurnstileToken("");
      }
    },
    (invalid) => {
      /* onInvalid: without this, RHF silently discards the async callback when
         zod validation fails and clicking "Изпрати" looks like a dead button.
         Jump to the step of the first invalid field so the red border is on
         screen, and surface a message next to the button. */
      const firstBad = Object.keys(invalid)[0] as keyof ApplicationInput | undefined;
      if (firstBad) {
        const stepIndex = STEP_FIELDS.findIndex((fields) => fields.includes(firstBad));
        if (stepIndex >= 0) setStep(stepIndex);
      }
      setSubmitError(t("errors.fixFieldsBelow" as any));
    },
  );

  if (result) return <ContractIssued result={result} values={form.getValues()} />;

  return (
    <FormProvider {...form}>
      <Card className="relative overflow-visible rounded-[18px] shadow-lg">
        {/* Loading overlay while the browser waits for the server to render the
            contract and send the email. The submit path can take a few seconds
            in prod (LibreOffice + SMTP), so a spinner + wait message is the
            difference between "did it work?" and confidence. */}
        {form.formState.isSubmitting && (
          <div
            role="status"
            aria-live="polite"
            className="absolute inset-0 z-20 flex flex-col items-center justify-center gap-4 rounded-[18px] bg-white/85 backdrop-blur-sm"
          >
            <Loader2 className="h-10 w-10 animate-spin text-primary" aria-hidden />
            <p className="max-w-[380px] px-4 text-center text-sm font-semibold text-navy-800">
              {t("nav.submittingLong")}
            </p>
          </div>
        )}

        <Stepper step={step} onJump={(i) => i < step && setStep(i)} />

        <header className="flex flex-wrap items-baseline gap-3 px-7 pt-5">
          <h2 className="font-display text-[22px] uppercase text-navy-700">
            {t(`steps.${STEP_KEYS[step]}.title`)}
          </h2>
          <span className="font-mono text-xs tracking-wider text-muted-foreground">
            {t("stepIndicator", { current: step + 1, total: 4 })}
          </span>
        </header>

        <form onSubmit={onSubmit} noValidate className="px-7 pb-2 pt-4">
          {step === 0 && <PersonalStep />}
          {step === 1 && <EducationStep />}
          {step === 2 && <ProgramStep />}
          {step === 3 && <ContractStep onEdit={setStep} />}

          {step === 3 && config.turnstileSiteKey && (
            <div className="mt-4">
              <Turnstile
                siteKey={config.turnstileSiteKey}
                onToken={setTurnstileToken}
                onError={() => setSubmitError(t("errors.antibot.failed"))}
              />
            </div>
          )}

          {submitError && (
            <p role="alert" className="mt-4 text-sm font-semibold text-destructive">
              {submitError}
            </p>
          )}

          <div className="mt-5 flex flex-wrap items-center gap-3 border-t pt-4">
            {step > 0 && (
              <Button type="button" variant="outline" onClick={back}>
                {t("nav.back")}
              </Button>
            )}
            <div className="ml-auto flex items-center gap-4">
              {savedAt && (
                <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
                  <Check className="h-3.5 w-3.5" /> {t("nav.draftSaved")}
                </span>
              )}
              {step < 3 ? (
                <Button type="button" onClick={next}>
                  {t("nav.next")}
                </Button>
              ) : (
                <Button
                  type="submit"
                  disabled={
                    form.formState.isSubmitting ||
                    (config.turnstileSiteKey ? !turnstileToken : false)
                  }
                >
                  {form.formState.isSubmitting ? t("nav.submitting") : t("nav.submit")}
                </Button>
              )}
            </div>
          </div>
        </form>
      </Card>
    </FormProvider>
  );
}

/* ------------------------------------------------------------------ */
function Stepper({ step, onJump }: { step: number; onJump: (i: number) => void }) {
  const { t } = useTranslation("apply");
  return (
    <ol className="flex items-start px-7 pb-1 pt-6">
      {STEP_KEYS.map((key, i) => {
        const done = i < step,
          current = i === step;
        return (
          <li
            key={key}
            className={cn("flex min-w-0 flex-col gap-2", i < 3 ? "flex-1" : "flex-none")}
          >
            <div className="flex h-[34px] items-center">
              <button
                type="button"
                onClick={() => onJump(i)}
                disabled={!done}
                aria-current={current ? "step" : undefined}
                className={cn(
                  "grid h-[34px] w-[34px] flex-none place-items-center rounded-full border-2 font-mono text-[13px] font-bold transition",
                  done || current
                    ? "border-primary bg-primary text-primary-foreground"
                    : "border-border bg-background text-muted-foreground",
                  current && "ring-4 ring-primary/15",
                  done && "cursor-pointer",
                )}
              >
                {done ? <Check className="h-4 w-4" /> : i + 1}
              </button>
              {i < 3 && <span className={cn("h-0.5 flex-1", done ? "bg-primary" : "bg-border")} />}
            </div>
            <div className="pr-3">
              <div
                className={cn(
                  "font-display text-[12.5px] font-bold uppercase tracking-wide",
                  done || current ? "text-foreground" : "text-muted-foreground",
                )}
              >
                {t(`steps.${key}.label`)}
              </div>
              <div className="text-[11.5px] text-muted-foreground">{t(`steps.${key}.sub`)}</div>
            </div>
          </li>
        );
      })}
    </ol>
  );
}

/* ------------------------------------------------------------------ */
function TextField({
  name,
  label,
  hint,
  placeholder,
  latin,
  inputMode,
  type = "text",
  className,
}: {
  name: keyof ApplicationInput;
  label: string;
  hint?: string;
  placeholder?: string;
  latin?: boolean;
  inputMode?: "text" | "numeric" | "tel" | "email";
  type?: string;
  className?: string;
}) {
  const { t } = useTranslation("apply");
  const {
    register,
    formState: { errors },
  } = useFormContext<ApplicationInput>();
  const error = errors[name]?.message as string | undefined;
  return (
    <div className={cn("flex flex-col gap-1.5", className)}>
      <Label htmlFor={name} className="text-[13px] font-bold">
        {label} <span className="text-primary">*</span>
      </Label>
      <Input
        id={name}
        type={type}
        inputMode={inputMode}
        placeholder={placeholder}
        aria-invalid={!!error}
        aria-describedby={error ? `${name}-error` : hint ? `${name}-hint` : undefined}
        autoComplete="off"
        spellCheck={false}
        className={cn(
          latin && "font-mono uppercase tracking-wide",
          error && "border-destructive focus-visible:ring-destructive/30",
        )}
        {...register(name)}
      />
      {error ? (
        <p id={`${name}-error`} role="alert" className="text-xs font-semibold text-destructive">
          {t(error as any)}
        </p>
      ) : (
        hint && (
          <p id={`${name}-hint`} className="text-xs text-muted-foreground">
            {hint}
          </p>
        )
      )}
    </div>
  );
}

function PhoneField({ className }: { className?: string }) {
  const { t } = useTranslation("apply");
  const {
    control,
    formState: { errors },
  } = useFormContext<ApplicationInput>();
  const error = errors.phone?.message as string | undefined;
  return (
    <div className={cn("flex flex-col gap-1.5", className)}>
      <Label htmlFor="phone" className="text-[13px] font-bold">
        {t("fields.phone")} <span className="text-primary">*</span>
      </Label>
      <Controller
        control={control}
        name="phone"
        render={({ field }) => {
          const digits = (field.value || "")
            .replace(/^\+359/, "")
            .replace(/\D/g, "")
            .slice(0, 9);
          return (
            <div
              className={cn(
                "flex h-9 w-full items-stretch overflow-hidden rounded-md border border-input bg-transparent text-sm shadow-sm transition-colors",
                "focus-within:outline-none focus-within:ring-1 focus-within:ring-ring",
                error && "border-destructive focus-within:ring-destructive/30",
              )}
            >
              {/* „+359" не може да се трие, това не е input, а фиксиран етикет */}
              <span
                aria-hidden
                className="grid select-none place-items-center border-r border-input bg-muted px-3 font-mono text-muted-foreground"
              >
                +359
              </span>
              <input
                id="phone"
                type="tel"
                inputMode="numeric"
                maxLength={9}
                placeholder="883 123 456"
                autoComplete="on"
                spellCheck={false}
                aria-invalid={!!error}
                aria-describedby={error ? "phone-error" : undefined}
                className="min-w-0 flex-1 bg-transparent px-3 font-mono outline-none placeholder:text-muted-foreground/60"
                value={digits}
                onBlur={field.onBlur}
                onChange={(e) => {
                  const next = e.target.value.replace(/\D/g, "").slice(0, 9);
                  field.onChange(`+359${next}`);
                }}
              />
            </div>
          );
        }}
      />
      {error && (
        <p id="phone-error" role="alert" className="text-xs font-semibold text-destructive">
          {t(error as any)}
        </p>
      )}
    </div>
  );
}

function PersonalStep() {
  const { t } = useTranslation("apply");
  const {
    control,
    watch,
    formState: { errors },
  } = useFormContext<ApplicationInput>();

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-12">
      <TextField
        name="email"
        label={t("fields.email")}
        type="email"
        inputMode="email"
        placeholder="ivan.petrov@gmail.com"
        hint={t("fields.emailHint")}
        className="md:col-span-12"
      />

      <TextField
        name="firstName"
        label={t("fields.firstName")}
        latin
        placeholder="IVAN"
        hint={t("fields.latinHint")}
        className="md:col-span-4"
      />
      <TextField
        name="middleName"
        label={t("fields.middleName")}
        latin
        placeholder="PETROV"
        className="md:col-span-4"
      />
      <TextField
        name="lastName"
        label={t("fields.lastName")}
        latin
        placeholder="DIMITROV"
        className="md:col-span-4"
      />

      <PhoneField className="md:col-span-4" />

      <div className="md:col-span-4">
        <Controller
          control={control}
          name="dateOfBirth"
          render={({ field }) => (
            <DateOfBirthPicker
              id="dateOfBirth"
              label={t("fields.dateOfBirth")}
              value={field.value}
              onChange={field.onChange}
              season={watch("season")}
              error={errors.dateOfBirth?.message as string}
            />
          )}
        />
      </div>

      <div className="md:col-span-4">
        <Controller
          control={control}
          name="placeOfBirth"
          render={({ field }) => (
            <AutocompleteField
              id="placeOfBirth"
              kind="cities"
              label={t("fields.placeOfBirth")}
              value={field.value}
              onChange={field.onChange}
              onBlur={field.onBlur}
              placeholder={t("autocomplete.startTyping")}
              error={errors.placeOfBirth?.message as string}
            />
          )}
        />
      </div>

      <TextField
        name="egn"
        label={t("fields.egn")}
        inputMode="numeric"
        placeholder="10 цифри"
        hint={t("fields.egnHint")}
        className="md:col-span-6"
      />
      <TextField
        name="idCardNumber"
        label={t("fields.idCard")}
        inputMode="numeric"
        placeholder="9 цифри"
        className="md:col-span-6"
      />
    </div>
  );
}

function EducationStep() {
  const { t } = useTranslation("apply");
  const {
    control,
    register,
    formState: { errors },
  } = useFormContext<ApplicationInput>();
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-12">
      <div className="md:col-span-12">
        <Controller
          control={control}
          name="university"
          render={({ field }) => (
            <AutocompleteField
              id="university"
              kind="universities"
              label={t("fields.university")}
              value={field.value}
              onChange={field.onChange}
              onBlur={field.onBlur}
              placeholder={t("autocomplete.startTypingUni")}
              hint={t("fields.universityHint")}
              error={errors.university?.message as string}
            />
          )}
        />
      </div>
      <div className="md:col-span-8">
        <Controller
          control={control}
          name="major"
          render={({ field }) => (
            <AutocompleteField
              id="major"
              kind="majors"
              label={t("fields.major")}
              value={field.value}
              onChange={field.onChange}
              onBlur={field.onBlur}
              placeholder={t("autocomplete.startTyping")}
              error={errors.major?.message as string}
            />
          )}
        />
      </div>
      <div className="flex flex-col gap-1.5 md:col-span-4">
        <Label htmlFor="yearOfStudy" className="text-[13px] font-bold">
          {t("fields.yearOfStudy")} <span className="text-primary">*</span>
        </Label>
        <select
          id="yearOfStudy"
          {...register("yearOfStudy")}
          className="h-[42px] rounded-lg border-[1.5px] border-input bg-background px-3 text-[15px]"
        >
          <option value="">{t("fields.choose")}</option>
          {(["1", "2", "3", "4", "master"] as const).map((y) => (
            <option key={y} value={y}>
              {t(`fields.yearOptions.${y}`)}
            </option>
          ))}
        </select>
        {errors.yearOfStudy && (
          <p role="alert" className="text-xs font-semibold text-destructive">
            {t(errors.yearOfStudy.message as any)}
          </p>
        )}
      </div>
    </div>
  );
}

function ProgramStep() {
  const { t } = useTranslation("apply");
  const { watch, setValue } = useFormContext<ApplicationInput>();
  const option = watch("programOption"),
    office = watch("office"),
    season = watch("season");

  const Choice = ({
    on,
    onClick,
    title,
    desc,
    price,
  }: {
    on: boolean;
    onClick: () => void;
    title: string;
    desc: string;
    price?: string;
  }) => (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={on}
      className={cn(
        "flex items-start gap-3 rounded-xl border-[1.5px] bg-background p-4 text-left transition",
        on ? "border-primary bg-primary/5" : "border-border hover:border-navy-500",
      )}
    >
      <span
        className={cn(
          "mt-0.5 h-[19px] w-[19px] flex-none rounded-full border-2",
          on ? "border-primary bg-primary shadow-[inset_0_0_0_3px_white]" : "border-border",
        )}
      />
      <span className="min-w-0">
        <span className="block text-sm font-bold">{title}</span>
        <span className="block text-[12.5px] text-muted-foreground">{desc}</span>
      </span>
      {price && <span className="ml-auto font-mono text-sm font-bold text-primary">{price}</span>}
    </button>
  );

  return (
    <div className="flex flex-col gap-5">
      <fieldset className="flex flex-col gap-2.5">
        <legend className="mb-2 text-[13px] font-bold">
          {t("fields.programOption")} <span className="text-primary">*</span>
        </legend>
        <Choice
          on={option === "full_arranged"}
          onClick={() => setValue("programOption", "full_arranged")}
          title="FULL ARRANGED"
          desc={t("program.fullDesc")}
          price="$1750"
        />
        <Choice
          on={option === "self_arranged"}
          onClick={() => setValue("programOption", "self_arranged")}
          title="SELF ARRANGED"
          desc={t("program.selfDesc")}
          price="$1250"
        />
        <p className="text-xs text-muted-foreground">{t("program.optionNote")}</p>
      </fieldset>

      <fieldset className="flex flex-col gap-2.5">
        <legend className="mb-2 text-[13px] font-bold">
          {t("fields.office")} <span className="text-primary">*</span>
        </legend>
        <Choice
          on={office === "varna"}
          onClick={() => setValue("office", "varna")}
          title={t("offices.varna")}
          desc={t("offices.varnaAddress")}
        />
        <Choice
          on={office === "sofia"}
          onClick={() => setValue("office", "sofia")}
          title={t("offices.sofia")}
          desc={t("offices.sofiaAddress")}
        />
      </fieldset>

      {/* Сезонът НЕ се избира — записваме винаги за предстоящото лято. */}
      <div className="flex flex-col gap-1.5">
        <span className="text-[13px] font-bold">{t("fields.season")}</span>
        <div className="flex items-center gap-2.5 rounded-xl border-[1.5px] bg-muted px-4 py-3">
          <Sun className="h-4 w-4 text-navy-700" />
          <b className="font-display text-[15px] uppercase tracking-wide text-navy-700">
            {t("fields.seasonOption", { year: season })}
          </b>
          <span className="text-[12.5px] text-muted-foreground">{t("fields.seasonFixed")}</span>
        </div>
        <p className="text-xs text-muted-foreground">
          {t("fields.seasonNextOpens", { next: Number(season) + 1, current: season })}
        </p>
      </div>
    </div>
  );
}

function ContractStep({ onEdit }: { onEdit: (step: number) => void }) {
  const { t } = useTranslation("apply");
  const {
    watch,
    register,
    formState: { errors },
  } = useFormContext<ApplicationInput>();
  const v = watch();

  const Row = ({ label, value, mono }: { label: string; value?: string; mono?: boolean }) => (
    <>
      <dt className="border-t px-4 py-2 text-[13px] text-muted-foreground">{label}</dt>
      <dd
        className={cn(
          "m-0 border-t px-4 py-2 text-[13.5px] font-semibold break-words",
          mono && "font-mono",
        )}
      >
        {value || "—"}
      </dd>
    </>
  );

  const Consent = ({
    name,
    children,
  }: {
    name: "acceptsTerms" | "declaresTruth" | "acceptsGdpr";
    children: ReactNode;
  }) => {
    const err = errors[name]?.message as string | undefined;
    return (
      <div className="flex flex-col gap-1.5">
        <label
          className={cn(
            "flex cursor-pointer items-start gap-3 rounded-xl border-[1.5px] p-4 text-[13.5px] text-muted-foreground",
            err ? "border-destructive" : "border-border",
          )}
        >
          <input
            type="checkbox"
            {...register(name)}
            className="mt-0.5 h-[19px] w-[19px] accent-[#A31D1A]"
          />
          <span>{children}</span>
        </label>
        {err && (
          <p role="alert" className="pl-4 text-xs font-semibold text-destructive">
            {t(err as never)}
          </p>
        )}
      </div>
    );
  };

  return (
    <div className="flex flex-col gap-4">
      <section className="overflow-hidden rounded-xl border">
        <h4 className="flex bg-muted px-4 py-2.5 text-xs font-bold uppercase tracking-wider text-muted-foreground">
          {t("review.personal")}
          <button
            type="button"
            onClick={() => onEdit(0)}
            className="ml-auto text-xs font-bold normal-case text-primary"
          >
            {t("review.edit")}
          </button>
        </h4>
        <dl className="m-0 grid grid-cols-[1fr_1.3fr]">
          <Row
            label={t("fields.threeNames")}
            value={[v.firstName, v.middleName, v.lastName].filter(Boolean).join(" ")}
            mono
          />
          <Row label={t("fields.email")} value={v.email} />
          <Row label={t("fields.phone")} value={v.phone} mono />
          <Row label={t("fields.dateOfBirth")} value={v.dateOfBirth} mono />
          <Row label={t("fields.placeOfBirth")} value={v.placeOfBirth} />
          {/* Маскираме — на екрана няма причина да стоят пълните идентификатори */}
          <Row label={t("fields.egn")} value={v.egn && `${v.egn.slice(0, 6)}••••`} mono />
          <Row
            label={t("fields.idCard")}
            value={v.idCardNumber && `•••••${v.idCardNumber.slice(-4)}`}
            mono
          />
        </dl>
      </section>

      <section className="overflow-hidden rounded-xl border">
        <h4 className="flex bg-muted px-4 py-2.5 text-xs font-bold uppercase tracking-wider text-muted-foreground">
          {t("review.education")}
          <button
            type="button"
            onClick={() => onEdit(1)}
            className="ml-auto text-xs font-bold normal-case text-primary"
          >
            {t("review.edit")}
          </button>
        </h4>
        <dl className="m-0 grid grid-cols-[1fr_1.3fr]">
          <Row label={t("fields.university")} value={v.university} />
          <Row label={t("fields.major")} value={v.major} />
          <Row
            label={t("fields.yearOfStudy")}
            value={v.yearOfStudy && t(`fields.yearOptions.${v.yearOfStudy}`)}
          />
          <Row
            label={t("fields.programOption")}
            value={
              v.programOption === "full_arranged"
                ? "FULL ARRANGED · $1750"
                : "SELF ARRANGED · $1250"
            }
          />
          <Row label={t("fields.season")} value={t("fields.seasonOption", { year: v.season })} />
          <Row label={t("fields.office")} value={t(`offices.${v.office}`)} />
        </dl>
      </section>

      <fieldset className="flex flex-col gap-2.5">
        <legend className="mb-2 text-[13px] font-bold">
          {t("consent.legend")} <span className="text-primary">*</span>
        </legend>
        <Consent name="acceptsTerms">{t("consent.terms")}</Consent>
        <Consent name="declaresTruth">{t("consent.truth")}</Consent>
        <Consent name="acceptsGdpr">{t("consent.gdpr")}</Consent>
      </fieldset>

      <aside className="rounded-xl bg-slate-50 p-5">
        <h3 className="mb-3 font-display text-[13px] uppercase tracking-wider text-navy-700">
          {t("whatHappens.title")}
        </h3>
        <ol className="grid list-none gap-2 p-0 [counter-reset:n]">
          {(["reserve", "email", "photo", "agent"] as const).map((k) => (
            <li
              key={k}
              className="relative pl-8 text-[13.5px] [counter-increment:n]
              before:absolute before:left-0 before:top-0.5 before:grid before:h-[21px] before:w-[21px]
              before:place-items-center before:rounded-full before:bg-primary before:font-mono
              before:text-[11px] before:font-bold before:text-white before:content-[counter(n)]"
            >
              {t(`whatHappens.${k}`, {
                email: v.email,
                office: t(`offices.${v.office}`),
                season: v.season,
              })}
            </li>
          ))}
        </ol>
      </aside>
    </div>
  );
}
