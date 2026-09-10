import js from "@eslint/js";
import globals from "globals";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import tseslint from "typescript-eslint";
import prettierConfig from "eslint-config-prettier";

/**
 * ESLint 9 flat config.
 *
 * Prettier owns formatting (see .prettierrc.json). ESLint owns correctness
 * and React-specific rules. eslint-config-prettier is included LAST so it
 * turns off any stylistic rules that would fight Prettier.
 *
 * Import organization on save is handled by the TypeScript language service
 * (VSCode setting "source.organizeImports": "explicit"), which sorts imports
 * and removes unused ones without needing a separate ESLint plugin.
 */
export default tseslint.config(
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
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      "react-refresh/only-export-components": [
        "warn",
        { allowConstantExport: true },
      ],
    },
  },
  prettierConfig,
);
