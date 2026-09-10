import { useCallback, useEffect, useMemo, useRef, useState } from "react";

/* ---------------------------------------------------------------
   useDebouncedValue — забавя въвеждането на стойност в дадено поле, не самото писане.
   Полето остава контролирано; забавя се само това,
   което е скъпо: валидацията, заявката за autocomplete, автозаписът.
   --------------------------------------------------------------- */
export function useDebouncedValue<T>(value: T, delay = 300): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(id);
  }, [value, delay]);
  return debounced;
}

/** Стабилна debounce-ната функция — за автозапис на чернова и телеметрия. */
export function useDebouncedCallback<A extends unknown[]>(
  fn: (...args: A) => void,
  delay = 500
) {
  const ref = useRef(fn);
  ref.current = fn;
  const timer = useRef<ReturnType<typeof setTimeout>>();
  useEffect(() => () => clearTimeout(timer.current), []);
  return useCallback((...args: A) => {
    clearTimeout(timer.current);
    timer.current = setTimeout(() => ref.current(...args), delay);
  }, [delay]);
}

import { api, type Suggestion } from "./api";

export type { Suggestion };

/* ---------------------------------------------------------------
   useSuggestions — autocomplete с debounce, отмяна на изпреварени
   заявки (AbortController) и кеш по заявка.
   Извиква GET /api/v1/lookup/{kind}?q=…
   --------------------------------------------------------------- */
export function useSuggestions(
  kind: "universities" | "cities" | "majors",
  query: string,
  { minChars = 2, delay = 250 } = {}
) {
  const debouncedQuery = useDebouncedValue(query.trim(), delay);
  const [items, setItems] = useState<Suggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const cache = useRef(new Map<string, Suggestion[]>());

  useEffect(() => {
    if (debouncedQuery.length < minChars) { setItems([]); setLoading(false); return; }

    const key = `${kind}:${debouncedQuery.toLowerCase()}`;
    const cached = cache.current.get(key);
    if (cached) { setItems(cached); setLoading(false); return; }

    const ctrl = new AbortController();
    setLoading(true);
    api.lookup(kind, debouncedQuery, ctrl.signal)
      .then((data) => { cache.current.set(key, data); setItems(data); })
      .catch((e) => { if ((e as Error)?.name !== "AbortError") setItems([]); })
      .finally(() => setLoading(false));

    return () => ctrl.abort();       // изпреварените заявки не пишат в state
  }, [kind, debouncedQuery, minChars]);

  /* Показваме „зареждам“, докато потребителят още пише — иначе списъкът мига. */
  const stale = query.trim() !== debouncedQuery;
  return useMemo(() => ({ items, loading: loading || stale }), [items, loading, stale]);
}
