import { KeyboardEvent, useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { Check, Loader2 } from "lucide-react";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Popover, PopoverAnchor, PopoverContent } from "@/components/ui/popover";
import { cn } from "@/lib/utils";
import { useSuggestions } from "../hooks/hooks";

type AutocompleteFieldProps = {
  id: string;
  label: string;
  value: string;
  onChange: (v: string) => void;
  onBlur?: () => void;
  kind: "universities" | "cities" | "majors";
  error?: string;
  hint?: string;
  placeholder?: string;
  required?: boolean;
};

/**
 * Свободен текст + подсказки. Съзнателно НЕ е select:
 * ако студентът учи в чужбина, ВУЗ-ът му няма да е в справочника,
 * затова списъкът само помага, но не ограничава.
 */
export function AutocompleteField({
  id,
  label,
  value,
  onChange,
  onBlur,
  kind,
  error,
  hint,
  placeholder,
  required = true,
}: AutocompleteFieldProps) {
  const { t } = useTranslation("apply");
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const { items, loading } = useSuggestions(kind, value);

  useEffect(() => setActive(0), [items]);
  const canOpen = open && value.trim().length >= 2;

  const commit = (v: string) => {
    onChange(v);
    setOpen(false);
    inputRef.current?.focus();
  };

  const onKeyDown = (e: KeyboardEvent) => {
    if (!canOpen || !items.length) return;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActive((i) => (i + 1) % items.length);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActive((i) => (i - 1 + items.length) % items.length);
    } else if (e.key === "Enter") {
      e.preventDefault();
      commit(items[active].value);
    } else if (e.key === "Escape") setOpen(false);
  };

  const describedBy = error ? `${id}-error` : hint ? `${id}-hint` : undefined;

  return (
    <div className="flex flex-col gap-1.5">
      <Label htmlFor={id} className="text-[13px] font-bold">
        {label} {required && <span className="text-primary">*</span>}
      </Label>

      <Popover open={canOpen} onOpenChange={setOpen}>
        <PopoverAnchor asChild>
          <div className="relative">
            <Input
              id={id}
              ref={inputRef}
              value={value}
              placeholder={placeholder}
              autoComplete="off"
              role="combobox"
              aria-expanded={canOpen}
              aria-autocomplete="list"
              aria-controls={`${id}-listbox`}
              aria-invalid={!!error}
              aria-describedby={describedBy}
              onChange={(e) => {
                onChange(e.target.value);
                setOpen(true);
              }}
              onFocus={() => setOpen(true)}
              onBlur={onBlur}
              onKeyDown={onKeyDown}
              className={cn(error && "border-destructive focus-visible:ring-destructive/30")}
            />
            {loading && (
              <Loader2 className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 animate-spin text-muted-foreground" />
            )}
          </div>
        </PopoverAnchor>

        <PopoverContent
          id={`${id}-listbox`}
          align="start"
          className="w-[--radix-popover-trigger-width] p-1"
          onOpenAutoFocus={(e) => e.preventDefault()} /* фокусът остава в полето */
        >
          <Command shouldFilter={false}>
            <CommandList>
              {loading && !items.length && (
                <div className="px-3 py-2 text-sm text-muted-foreground">
                  {t("autocomplete.loading")}
                </div>
              )}
              {!loading && !items.length && (
                <CommandEmpty className="px-3 py-2 text-sm italic text-muted-foreground">
                  {t("autocomplete.noMatch")}
                </CommandEmpty>
              )}
              <CommandGroup>
                {items.map((s, i) => (
                  <CommandItem
                    key={s.value}
                    value={s.value}
                    onMouseDown={(e) => e.preventDefault()} /* да не blur-не полето */
                    onSelect={() => commit(s.value)}
                    className={cn("cursor-pointer", i === active && "bg-accent")}
                  >
                    <div className="min-w-0">
                      <div className="truncate">{highlight(s.label, value)}</div>
                      {s.hint && (
                        <div className="text-[11.5px] text-muted-foreground">{s.hint}</div>
                      )}
                    </div>
                    {s.value === value && <Check className="ml-auto h-4 w-4 text-primary" />}
                  </CommandItem>
                ))}
              </CommandGroup>
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>

      {error ? (
        <p id={`${id}-error`} role="alert" className="text-xs font-semibold text-destructive">
          {t(error as any)}
        </p>
      ) : (
        hint && (
          <p id={`${id}-hint`} className="text-xs text-muted-foreground">
            {hint}
          </p>
        )
      )}
    </div>
  );
}

function highlight(text: string, query: string) {
  const q = query.trim();
  if (!q) return text;
  const i = text.toLowerCase().indexOf(q.toLowerCase());
  if (i < 0) return text;
  return (
    <>
      {text.slice(0, i)}
      <mark className="bg-transparent font-bold text-primary">{text.slice(i, i + q.length)}</mark>
      {text.slice(i + q.length)}
    </>
  );
}
