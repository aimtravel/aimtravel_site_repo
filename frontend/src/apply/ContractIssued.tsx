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
        {result.emailSent ? t("success.emailSent", { email: result.emailSentTo }) : "Документите са създадени, но имейлът не е изпратен. Изтегли ги оттук и се свържи с нас."}
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
              option: values.programOption === "full_arranged" ? "PREMIUM FULL ARRANGED" : "SELF ARRANGED",
            })}
          </p>
          <p className="font-bold text-foreground">{t("email.nextStepsTitle")}</p>
          <ol className="grid list-decimal gap-1.5 pl-5">
            <li>{t("email.steps.sign")}</li>
            <li className="py-2"><Button asChild><a href="https://aimtravel.bg/application-form/">{t("email.steps.forms")}</a></Button></li>
            <li className="space-y-2"><p>{t("email.steps.deposit", {amount: values.saveExchange ? 481 : 232})}</p>
              <div className="rounded-lg bg-slate-50 p-3 leading-relaxed text-navy-800">
                <p>IBAN: <strong className="break-all">BG60UNCR70001523205219</strong></p>
                <p>УниКредит Булбанк АД</p>
                <p>Получател: АГЕНЦИЯ ЗА МЕЖДУНАРОДНА МОБИЛНОСТ ООД</p>
                <p>Основание: {result.contractNumber}</p>
              </div>
            </li>
            <li>{t("email.steps.photo")}</li>
          </ol>
          <div className="flex flex-wrap gap-2 pt-1">
            {[`Dogovor_${result.contractNumber}.pdf`, ...(values.saveExchange ? [`Annex_${result.contractNumber}.pdf`] : []), "AIM_Bank_Details.pdf"].map(
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
          <div className="border-t pt-4"><p className="mb-3 font-bold text-navy-800">Насреща сме</p>
            <div className="flex flex-wrap gap-2">
              <Button asChild className="bg-[#665cac] text-white hover:bg-[#554b96]"><a href="viber://chat?number=%2B359889966583">Viber</a></Button>
              <Button asChild className="bg-[#a22c67] text-white hover:bg-[#872456]"><a href="https://www.instagram.com/aimtravel_usa/">Instagram</a></Button>
              <Button asChild className="bg-[#1864bd] text-white hover:bg-[#14539e]"><a href="https://www.facebook.com/profile.php?id=100072235954652">Facebook</a></Button>
            </div>
          </div>
        </div>
      </section>

      <div className="mt-6 flex flex-wrap justify-center gap-3">
        <Button asChild>
          <a href={result.contractPdfUrl} download>
            <Download className="mr-2 h-4 w-4" /> {t("success.download")}
          </a>
        </Button>
        {result.annexPdfUrl && <Button asChild variant="outline"><a href={result.annexPdfUrl} download>Изтегли анекса (PDF)</a></Button>}
      </div>
    </Card>
  );
}
