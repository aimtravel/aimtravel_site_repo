import { useTranslation } from "react-i18next";
import { Check, Download, Mail, Paperclip } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { ContractResult } from "../api/api";
import type { ApplicationInput } from "../helpers/applySchema";

type ContractIssuedProps = {
  result: ContractResult;
  values: ApplicationInput;
};

export function ContractIssued({ result, values }: ContractIssuedProps) {
  const { t } = useTranslation("apply");
  const fullName = [values.firstName, values.middleName, values.lastName].filter(Boolean).join(" ");

  return (
    <Card className="rounded-[18px] px-8 py-11 text-center shadow-lg">
      <div className="mx-auto mb-5 grid h-[74px] w-[74px] place-items-center rounded-full bg-emerald-50">
        <Check className="h-8 w-8 text-emerald-700" />
      </div>

      <h2 className="font-display text-[26px] uppercase text-navy-700">{t("success.title")}</h2>
      <p className="mx-auto mt-3 max-w-[560px] text-[15px] font-semibold text-emerald-800">
        {t("success.emailSent", { email: result.emailSentTo })}
      </p>
      <p className="mx-auto mt-2.5 max-w-[520px] text-muted-foreground">
        {t("success.body", { name: values.firstName })}
      </p>

      <div className="mx-auto my-6 inline-flex flex-col gap-1 rounded-xl bg-navy-800 px-7 py-3.5 text-white">
        <span className="font-mono text-[11px] uppercase tracking-[0.14em] text-coral">
          {t("success.contractLabel")}
        </span>
        <strong className="font-mono text-[22px] tracking-wider">{result.contractNumber}</strong>
      </div>
      <p className="text-xs text-muted-foreground">{t("success.keepNumber")}</p>

      {/* Предварителен изглед на изпратения имейл — студентът вижда какво да очаква */}
      <section className="mx-auto mt-7 max-w-[640px] overflow-hidden rounded-xl border text-left">
        <header className="flex flex-wrap items-center gap-2 border-b bg-muted px-4 py-2.5 text-xs text-muted-foreground">
          <Mail className="h-4 w-4" />
          <span>
            <b>{t("success.mailTo")}</b> {result.emailSentTo}
          </span>
          <span>·</span>
          <span>
            <b>{t("success.mailSubject")}</b>{" "}
            {t("email.subject", { contractNumber: result.contractNumber, season: values.season })}
          </span>
        </header>
        <div className="grid gap-3 p-4 text-[13.5px] text-muted-foreground">
          <p>{t("email.greeting", { name: fullName })}</p>
          <p>
            {t("email.concluded", {
              contractNumber: result.contractNumber,
              option: values.programOption === "full_arranged" ? "FULL ARRANGED" : "SELF ARRANGED",
            })}
          </p>
          <p className="font-bold text-foreground">{t("email.nextStepsTitle")}</p>
          <ol className="grid list-decimal gap-1.5 pl-5">
            {(["sign", "photo", "forms", "deposit"] as const).map((k) => (
              <li key={k}>{t(`email.steps.${k}`)}</li>
            ))}
          </ol>
          <div className="flex flex-wrap gap-2 pt-1">
            {[`Dogovor_${result.contractNumber}.pdf`, "AIM_Travel_Application_Form.pdf"].map(
              (f) => (
                <span
                  key={f}
                  className="inline-flex items-center gap-1.5 rounded-md border bg-muted px-2.5 py-1.5 font-mono text-xs"
                >
                  <Paperclip className="h-3.5 w-3.5" /> {f}
                </span>
              ),
            )}
          </div>
        </div>
      </section>

      <div className="mt-6 flex flex-wrap justify-center gap-3">
        <Button asChild>
          <a href={result.contractPdfUrl} download>
            <Download className="mr-2 h-4 w-4" /> {t("success.download")}
          </a>
        </Button>
      </div>
    </Card>
  );
}
