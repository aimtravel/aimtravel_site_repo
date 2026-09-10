import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { I18nextProvider } from "react-i18next";

import i18n from "@/i18n";
import { ApplyPage } from "@/apply/ApplyPage";
import "@/styles/tokens.css";

/**
 * Entry point за „остров“ в Django template.
 *
 * Не е SPA: намираме контейнера, който Django е отрендерил, и монтираме само
 * него. Ако елементът липсва, не гърмим — същият bundle може да бъде
 * включен в base template.
 */
const container = document.getElementById("apply-root");

if (container) {
  // data-* атрибутите идват от Django и спестяват един HTTP request при зареждане.
  const bootstrap = JSON.parse(container.dataset.bootstrap ?? "{}");

  createRoot(container).render(
    <StrictMode>
      <I18nextProvider i18n={i18n}>
        <ApplyPage bootstrap={bootstrap} />
      </I18nextProvider>
    </StrictMode>,
  );
}
