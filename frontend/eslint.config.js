import js from "@eslint/js";
import { defineConfig } from "eslint/config";
import prettierConfig from "eslint-config-prettier";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import unusedImports from "eslint-plugin-unused-imports";
import globals from "globals";
import tseslint from "typescript-eslint";

/**
 * ESLint 9 flat config.
 *
 * Разделение на отговорностите — това е ключово за да няма flicker на save:
 *   • Prettier (+ @ianvs/prettier-plugin-sort-imports) — форматиране И сортиране
 *     на импорти. Единственият източник на истина за импортния ред.
 *   • ESLint — коректност (react-hooks, ts правила) и premahvane на unused
 *     imports (заменя source.organizeImports, който преди се биеше с Prettier).
 *   • eslint-config-prettier е ПОСЛЕДЕН и изключва всички stylistic правила,
 *     които биха се сблъскали с Prettier.
 *
 * NB: НЕ включвай тук eslint-plugin-import с "import/order" или
 * "simple-import-sort" — това ще върне конфликта с Prettier plugin-а.
 */
export default defineConfig(
  { ignores: ["dist", "node_modules", "../static/dist"] },
  {
    files: ["**/*.{ts,tsx}"],
    extends: [js.configs.recommended, ...tseslint.configs.recommended],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
    },
    plugins: {
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh,
      "unused-imports": unusedImports,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      "react-refresh/only-export-components": ["warn", { allowConstantExport: true }],

      /* unused-imports поема ролята — изключваме дубликата от tseslint,
         иначе една и съща променлива се маркира два пъти. */
      "@typescript-eslint/no-unused-vars": "off",
      "unused-imports/no-unused-imports": "error",
      "unused-imports/no-unused-vars": [
        "warn",
        {
          vars: "all",
          varsIgnorePattern: "^_",
          args: "after-used",
          argsIgnorePattern: "^_",
        },
      ],
    },
  },
  prettierConfig,
);
