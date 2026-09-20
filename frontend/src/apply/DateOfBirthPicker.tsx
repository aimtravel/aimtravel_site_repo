import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { format, parseISO } from "date-fns";
import { bg } from "date-fns/locale";
import { CalendarIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import { Label } from "@/components/ui/label";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { cn } from "@/lib/utils";

type DateOfBirthPickerProps = {
  id: string;
  label: string;
  value?: string; // ISO: YYYY-MM-DD
  season: string; // подава се, но не се използва за ограничение на picker-a
  error?: string;
  onChange: (iso: string) => void;
};

/**
 * Date picker с широк прозорец 1900-01-01 → днес. Възрастовият критерий
 * от чл. 8.1.3 (18–28 г.) е изключен, за да може формата да се тества и
 * с произволна дата на раждане.
 */
export function DateOfBirthPicker({
  id,
  label,
  value,
  onChange,
  error,
}: DateOfBirthPickerProps) {
  const { t } = useTranslation("apply");
  const [open, setOpen] = useState(false);

  const { min, max, defaultMonth } = useMemo(() => {
    const min = new Date(1900, 0, 1);
    const max = new Date();
    return { min, max, defaultMonth: value ? parseISO(value) : max };
  }, [value]);

  return (
    <div className="flex flex-col gap-1.5">
      <Label htmlFor={id} className="text-[13px] font-bold">
        {label} <span className="text-primary">*</span>
      </Label>

      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            id={id}
            type="button"
            variant="outline"
            aria-invalid={!!error}
            aria-describedby={error ? `${id}-error` : undefined}
            className={cn(
              "h-[42px] justify-start gap-2 border-[1.5px] px-3 font-normal",
              !value && "text-muted-foreground",
              error && "border-destructive focus-visible:ring-destructive/30",
            )}
          >
            <CalendarIcon className="h-4 w-4" />
            {value
              ? format(parseISO(value), "d MMMM yyyy 'г.'", { locale: bg })
              : t("fields.dateOfBirthPlaceholder")}
          </Button>
        </PopoverTrigger>

        <PopoverContent align="start" className="w-auto p-0">
          <Calendar
            mode="single"
            locale={bg}
            weekStartsOn={1}
            captionLayout="dropdown"
            startMonth={min}
            endMonth={max}
            defaultMonth={defaultMonth}
            selected={value ? parseISO(value) : undefined}
            disabled={{ before: min, after: max }}
            onSelect={(d) => {
              if (d) {
                onChange(format(d, "yyyy-MM-dd"));
                setOpen(false);
              }
            }}
          />
        </PopoverContent>
      </Popover>

      {error && (
        <p id={`${id}-error`} role="alert" className="text-xs font-semibold text-destructive">
          {t(error as "errors.required")}
        </p>
      )}
    </div>
  );
}
