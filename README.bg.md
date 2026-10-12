# Сайтът на AIM Travel — aimtravel.bg

[English](README.md) · **Български**

Изходният код на https://aimtravel.bg — сайтът на AIM Travel (Summer Work & Travel USA и свързани програми):

- **Информация** — програмата WAT USA, оферти за работа, стажове, H-2B, новини, цени и контакти.
- **Профили** — след вход потребителите попълват регистрацията за WAT и заявлението за данъчно възстановяване.
- **Формуляр** „Запиши се за бригада“ (`/zapisvane-za-brigada/`) — React страница, която издава договора автоматично и го изпраща на кандидата по имейл.

Всяка промяна стига до живия сайт по един и същ начин: pull request към `main`, автоматични проверки, merge, автоматичен deploy. Никой не редактира файлове на сървъра.

> ⚠️ **Хранилището е публично.** Никога не commit-вай пароли, ключове, `credentials.py`, dump-ове на базата или каквото и да е с лични данни на кандидати (имена, ЕГН, номера на лични карти, договори).

## Съдържание

1. [Какво къде е](#1-какво-къде-е)
2. [Бекенд (Django) — локална настройка](#2-бекенд-django--локална-настройка)
3. [Фронтенд (React) — локална настройка](#3-фронтенд-react--локална-настройка)
4. [Продукция — Superhosting cPanel](#4-продукция--superhosting-cpanel)
5. [Промяна — pull request, преглед, merge](#5-промяна--pull-request-преглед-merge)

---

## 1. Какво къде е

| Път | Какво е |
|---|---|
| `aimtravel_site/` | Django проектът: `settings.py`, `urls.py` и приложенията `web`, `main_page`, `posting`, `taxes`, `user_auth`, `user_profile`, `apply` (формулярът) |
| `templates/` | Django шаблони. В `templates/apply/documents/` са шаблонът на договора за сезона (`contract_<сезон>.docx`) и празните бланки, които се изпращат с всеки договор |
| `static/` | CSS, JS и изображения. На сървъра се събират в `public_html/static` |
| `frontend/` | React + TypeScript + Vite приложението на формуляра. Build-ът му отива в `static/dist/`, който **не е** в git — CI го build-ва |
| `tests/` | UI smoke тестове (всяка публична страница трябва да се зарежда) и end-to-end тест на формуляра |
| `requirements-production.txt` | Точните Python пакети, инсталирани на продукция. **Единственият requirements файл, който се ползва** |
| `deploy/production_deploy.sh`, `.cpanel.yml` | Скриптът за deploy, който се изпълнява на сървъра |
| `.github/workflows/` | `ci.yml` (проверки за всеки pull request) и `deploy-production.yml` (deploy при всеки merge в `main`) |
| `Инструкция за ползване на AIM TRAVEL USA site.pdf` / `.docx` | Ръководство за редактиране на съдържанието на сайта през Django admin |

Останали от стария проект — **не ги ползвай и не добавяй към тях**: `requirements.txt` (стар списък в UTF-16), `venv/` (стара Windows виртуална среда), `staticfiles/`, `media/`, `private_media/`, `aimtravel_site_repo.rar`, `.idea/` и следените в git файлове `__pycache__/*.pyc`.

---

## 2. Бекенд (Django) — локална настройка

На продукция работят **Python 3.11**, **Django 4.1** и **MariaDB 10.11**. Локално ползвай Python 3.11 и MySQL 8.4.

### 2.1 Инсталиране на инструментите (еднократно)

**macOS** (с [Homebrew](https://brew.sh)):

```bash
brew install python@3.11 mysql@8.4 pkgconf git
brew link --force mysql@8.4       # слага mysql и файловете му там, където MySQL драйверът ги търси
brew services start mysql@8.4     # пуска MySQL сега и при всяко влизане
```

**Windows**:

1. **Python 3.11** (64-bit) от https://www.python.org/downloads/ — отметни *„Add python.exe to PATH“*.
2. **MySQL 8.4 LTS Community Server** от https://dev.mysql.com/downloads/mysql/ (версия 8.4, *Windows (x86, 64-bit), MSI Installer*) — запомни паролата за `root`, която избереш.
3. **Git for Windows** от https://git-scm.com/download/win.

За командите за Windows по-долу ползвай **PowerShell**.

### 2.2 Изтегляне на кода

```bash
git clone https://github.com/aimtravel/aimtravel_site_repo.git
cd aimtravel_site_repo
```

### 2.3 Python виртуална среда

Създай я **извън** папката на хранилището (вътре в нея git би показал хиляди нови файлове).

macOS:

```bash
python3.11 -m venv ~/.venvs/aimtravel
source ~/.venvs/aimtravel/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-production.txt
```

Windows (PowerShell):

```powershell
py -3.11 -m venv $HOME\.venvs\aimtravel
& $HOME\.venvs\aimtravel\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-production.txt
```

Ако PowerShell откаже да изпълни `Activate.ps1`, изпълни веднъж `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` и опитай пак.

Активирай средата (реда `source …` / `& …Activate.ps1`) във всеки нов терминал, преди да пускаш `python manage.py …`.

Хранилището все още следи стари компилирани `.pyc` файлове и всяко пускане на Python ги показва като променени в `git status`. Предотврати го, като зададеш веднъж `PYTHONDONTWRITEBYTECODE=1`:

- macOS: `echo 'export PYTHONDONTWRITEBYTECODE=1' >> ~/.zshrc` и отвори нов терминал
- Windows: `setx PYTHONDONTWRITEBYTECODE 1` и отвори нов PowerShell

Ако все пак `.pyc` файлове се покажат като променени, върни ги с `git restore -- '*.pyc'`. Никога не ги commit-вай.

### 2.4 Локална база данни

Пусни MySQL клиента като `root`:

- macOS: `mysql -u root -p` (току-що инсталираният през Homebrew MySQL няма парола за root — просто натисни Enter)
- Windows: `& "C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe" -u root -p` (папката по подразбиране; промени я, ако си избрал друга)

После изпълни (с твоя локална парола):

```sql
CREATE DATABASE aimtravel CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'aimtravel'@'localhost' IDENTIFIED BY 'choose-a-local-password';
GRANT ALL PRIVILEGES ON aimtravel.* TO 'aimtravel'@'localhost';
-- тестовете създават и трият собствена база, test_aimtravel
GRANT ALL PRIVILEGES ON test_aimtravel.* TO 'aimtravel'@'localhost';
```

Излез с `exit`. Всеки разработчик започва с **празна** база. **Никога не копирай продукционната база** на компютъра си: в нея има лични данни на кандидати.

### 2.5 `credentials.py` (локални настройки)

`settings.py` съдържа стойностите за продукция; тайните и стойностите, специфични за машината, идват от `credentials.py` — файл до `manage.py`, който е в `.gitignore`. Създай го със:

```python
# Само за локална разработка. Файлът е в .gitignore: никога не го commit-вай.
from pathlib import Path

LOCAL_DATA = Path.home() / "aimtravel-local"  # качени файлове и договори, извън хранилището

SECRET_KEY = "local-development-only"
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

DB_NAME = "aimtravel"
DB_USER = "aimtravel"
DB_PASSWORD = "choose-a-local-password"   # паролата от стъпка 2.4
DB_HOST = "localhost"

EMAIL_HOST_USER = ""
EMAILPASSWORD = ""
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"  # имейлите се отпечатват в терминала

STATICFILES_DIRS = [Path(__file__).resolve().parent / "static"]
STATIC_ROOT = LOCAL_DATA / "static"
MEDIA_ROOT = LOCAL_DATA / "media"
APPLY_PRIVATE_ROOT = LOCAL_DATA / "private"
SITE_URL = "http://127.0.0.1:8000"
```

Задължителни са `SECRET_KEY`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `EMAIL_HOST_USER` и `EMAILPASSWORD`. Всичко останало пада на стойността за продукция, затова запази редовете по-горе — без тях Django би търсил `/home/aimtrave/public_html/…`. Другите незадължителни ключове са описани в [точка 4.3](#43-файлове-само-на-сървъра).

### 2.6 Таблици и администратор

```bash
python manage.py migrate
python manage.py createsuperuser      # пита за имейл и парола
python manage.py runserver
```

Отвори http://127.0.0.1:8000/admin/ и влез.

При празна база **началната страница, `/wat_usa/` и `/taxes/` показват грешка**, докато няма съдържание. В Django admin добави по един запис във всяко от:

- **Главна страница**: **1. Основен слайдер**, **2. Втори слайдер**, **3. Трети слайдер**, **4. Четвърти слайдер**, **5. Секция "За нас"**, **6. Секция "Call to Action"**, **7. Секция "Видеа"**, **8. Секция "Цени"**, **9. Секция "Услуги"**
- **Блог**: **Новини** (поне една новина)
- **Администрация**: **Цени**

След това http://127.0.0.1:8000/ работи.

### 2.7 Тестове и lint

```bash
python manage.py test tests
```

Очаквай `OK (expected failures=2)`: две страници вече не работят на живия сайт (`/prices/all/`, `/services/all/`) и са отбелязани като известни грешки.

Lint проверката на pull request-ите търси само грешки, които чупят кода, и само в Python файловете, които си променил:

```bash
pip install ruff==0.6.9
ruff check --select E9,F63,F7,F82 path/to/changed_file.py
```

### 2.8 Добре е да знаеш

- **Миграции**: моделите на няколко по-стари приложения леко се различават от историята на миграциите на продукция. Затова обикновено `python manage.py makemigrations` би създало нежелани миграции (и би спряло да пита за `news.slug`). Винаги посочвай приложението — напр. `python manage.py makemigrations apply` — и прочети създадения файл, преди да го commit-неш.
- **Имейлите** се отпечатват в терминала (console backend).
- **Формулярът**: Turnstile (защитата от ботове) е изключен локално. Без LibreOffice (`soffice`) договорът се създава като `.docx` вместо PDF — за разработка това е наред.
- **Нов Python пакет**: добави го с точна версия (`name==x.y.z`) в `requirements-production.txt`. Deploy-ът го инсталира на сървъра.

---

## 3. Фронтенд (React) — локална настройка

Страницата на формуляра (`/zapisvane-za-brigada/`) е React + TypeScript приложение във `frontend/`, build-вано с Vite и Tailwind. Django сервира страницата; приложението се зарежда в нея чрез [django-vite](https://github.com/MrBin99/django-vite).

### 3.1 Инсталиране

**Node.js 24 LTS** (версията, която ползва CI):

- macOS: `brew install node@24 && brew link --force node@24` (или с [nvm](https://github.com/nvm-sh/nvm): `nvm install 24`)
- Windows: *LTS* инсталаторът от https://nodejs.org/

После, от папката на хранилището:

```bash
cd frontend
npm ci        # инсталира точните версии от package-lock.json
```

### 3.2 Разработка

Пусни два терминала:

| Терминал 1 (папката на хранилището, активна среда) | Терминал 2 (`frontend/`) |
|---|---|
| `python manage.py runserver` | `npm run dev` |

Отвори **http://127.0.0.1:8000/zapisvane-za-brigada/** (адреса на Django, не на Vite). При `DEBUG = True` страницата зарежда приложението от dev сървъра на Vite (`http://127.0.0.1:5173`), така че промените във `frontend/src/` се виждат веднага.

### 3.3 Build

```bash
npm run build      # проверка на типовете + build в ../static/dist
```

`static/dist/` е в `.gitignore`: **никога не commit-вай резултата от build-а**. CI build-ва фронтенда за всеки pull request, а deploy-ът инсталира този build на сървъра.

За да провериш build-натата версия локално, добави `VITE_DEV_MODE = False` в `credentials.py`, изпълни `npm run build` и презареди страницата, докато работи само `runserver`. Махни реда, за да се върнеш в режим на разработка.

### 3.4 Скриптове

| Команда | Състояние |
|---|---|
| `npm run typecheck` | минава |
| `npm run build` | минава — това пуска CI („Frontend build“) |
| `npm run lint` | в момента не минава (1 предупреждение; не се допускат предупреждения) — CI още не го пуска |
| `npm run format:check` | в момента не минава (16 файла не са форматирани с Prettier) — CI още не го пуска |
| `npm test` | в момента не минава: още няма тестове за фронтенда |

Не commit-вай `frontend/node_modules/`; папката е в `.gitignore`.

---

## 4. Продукция — Superhosting cPanel

### 4.1 Как е хостнат

- Споделен хостинг в **Superhosting.bg** с **cPanel**. Django работи през **Passenger** („Setup Python App“), Python 3.11; базата е MariaDB 10.11.
- На сървъра **няма Node.js** — фронтендът се build-ва от GitHub Actions.
- **Няма staging сайт**: тествай локално, после merge.

| На сървъра | Път |
|---|---|
| Django приложението (`BASE_DIR`) | `/home/aimtrave/aimtravel_site` |
| Python виртуална среда | `/home/aimtrave/virtualenv/aimtravel_site/3.11` |
| Git копието, от което deploy-ва cPanel | `/home/aimtrave/repositories/aimtravel-production` |
| Събраните статични файлове (сервира ги уеб сървърът) | `/home/aimtrave/public_html/static` |
| Качени файлове (публични) | `/home/aimtrave/public_html/media` |
| Договори и попълнени формуляри (лични) | `/home/aimtrave/aimtravel_site/private_media/apply` |
| Резултатът от последния deploy | `~/deploy-state/last-deploy.txt` |
| Архиви от последните 5 deploy-а (код + база) | `~/deploy-backups/` |

### 4.2 Какво става при merge на pull request

Workflow-ът „Deploy to production“ (раздел Actions) се пуска при всеки push в `main`. Първо job-ът **tests** пуска проверките от `ci.yml` — Django check + UI smoke tests и build на фронтенда (Ruff се пуска само за pull request-и). После job-ът **deploy** минава през тези стъпки; таблицата в обобщението на изпълнението ползва същите номера:

1. **cPanel repo** — git копието на сървъра се намира през cPanel API.
2. **Frontend build** — build-ът от проверките се качва на сървъра заедно с контролна сума.
3. **Pull main** — git копието на сървъра се обновява до merge-натия commit.
4. **Deploy on server** — изпълнява се `deploy/production_deploy.sh`:
   архив на кода и базата → копиране на кода в приложението → инсталиране на build-а на фронтенда →
   `pip install` (само ако `requirements-production.txt` е променен) → `migrate` → `collectstatic` → `check` → рестарт.
   Ако някоя стъпка се провали, предишният код се връща автоматично.
5. **Live site check** — публичните страници трябва да отговарят на https://aimtravel.bg.
6. **Rollback** — само ако стъпка 5 се провали: кодът се възстановява от архива. Базата *не* се връща.

Отвори изпълнението (Actions → Deploy to production), за да видиш таблицата. Провалената стъпка показва причината; сгънатата група **„cPanel deploy log“** съдържа целия изход от сървъра. Ако докато едно изпълнение чака, `main` вече е напреднал, то не deploy-ва нищо и го казва — новият commit се deploy-ва от собственото си изпълнение.

За да deploy-неш `main` отново без нов commit: Actions → Deploy to production → **Run workflow** (клон `main`).

### 4.3 Файлове само на сървъра

Тези файлове съществуват само на сървъра и никога не са в git:

- **`/home/aimtrave/aimtravel_site/credentials.py`** (права `600`)
  - Задължителни: `SECRET_KEY`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `EMAIL_HOST_USER`, `EMAILPASSWORD`
  - `STATICFILES_DIRS` трябва да сочи папката `static` на приложението (`/home/aimtrave/aimtravel_site/static`)
  - Незадължителни за формуляра: `TURNSTILE_SITE_KEY` и `TURNSTILE_SECRET_KEY` (защитата от ботове е изключена, докато не са зададени и двата), `CONTRACT_EMAIL_BCC` (допълнителни скрити копия на всеки имейл с договор, напр. `["office@aimtravel.bg"]`), `AIM_FROM_EMAIL`, `SITE_URL`, `AIM_APPFORM_FONT_PATH` (`.ttf` шрифт с кирилица за попълнения PDF формуляр, ако на сървъра няма такъв)
- **`/home/aimtrave/aimtravel_site/wat_credentials.py`** — Google Sheets webhook-ът за регистрацията за WAT

За промяна го редактирай в cPanel **File Manager** или **Terminal**, после рестартирай приложението: `touch /home/aimtrave/aimtravel_site/tmp/restart.txt` (или бутона *Restart* в **Setup Python App**).

Workflow-ът влиза в cPanel с три тайни на хранилището (GitHub → Settings → Secrets and variables → Actions): `CPANEL_HOST`, `CPANEL_USER`, `CPANEL_TOKEN`. Токенът се създава в cPanel → **Security → Manage API Tokens**. За смяна: създай нов токен, обнови тайната, после изтрий стария токен.

### 4.4 Отмяна на лоша промяна

**Нормалният начин** — revert в GitHub: отвори merge-натия pull request → **Revert** → отваря се нов pull request → merge-ни го, когато проверките минат. Предишният код се deploy-ва като всяка друга промяна.

Промени в базата (миграции) **не** се отменят от revert или връщане назад. Архивът на базата от всеки deploy е в `~/deploy-backups/<час>-<commit>/db.sql.gz`; възстановяването му презаписва по-новите данни, затова го прави само съзнателно.

**Спешно** (сайтът не работи и revert-ът не може да чака проверките) — в cPanel **Terminal**:

```bash
ls ~/deploy-backups                     # избери папката отпреди лошия deploy
echo /home/aimtrave/deploy-backups/FOLDER > ~/deploy-state/ROLLBACK
cd ~/repositories/aimtravel-production && bash deploy/production_deploy.sh
cat ~/deploy-state/last-deploy.txt      # трябва да пише state=rolled_back
```

После направи и revert в GitHub — иначе следващият deploy ще върне промяната.

### 4.5 Правила

- **Не редактирай код на сървъра.** Всеки deploy презаписва `aimtravel_site/`, `templates/`, `static/` и файловете в корена със съдържанието на `main`.
- **Без тайни и лични данни в git** — хранилището е публично.
- **Новите Python пакети** се добавят в `requirements-production.txt` с точна версия.
- Преди формулярът да бъде свързан от публичните страници, ключовете за Turnstile трябва да са зададени в `credentials.py`.

---

## 5. Промяна — pull request, преглед, merge

`main` е защитен (ruleset **ruleForMain**, важи за всички, включително администраторите):

- промените стигат до `main` само през pull request — директен push се отхвърля;
- трябва да минат три проверки: **Django check + UI smoke tests**, **Frontend build**, **Ruff (changed Python files)**;
- преди merge клонът трябва да е обновен спрямо `main`;
- force push и изтриване на `main` са забранени;
- одобрения **не** са задължителни (0), но е силно препоръчително колега да прегледа промяната.

**Merge-ът deploy-ва на https://aimtravel.bg веднага.** Merge-вай само това, което е готово за живия сайт.

### 5.1 Нов клон

```bash
git switch main
git pull
git switch -c feature/short-description     # или fix/…, docs/…, ci/…
```

### 5.2 Промяна, тест, commit

```bash
python manage.py test tests                 # и npm run build, ако си променял frontend/
git status                                  # провери какво ще commit-неш
git add path/to/file1 path/to/file2         # добавяй файловете по име
git commit -m "Кратко описание на промяната"
```

Преди commit се увери, че `git status` не показва нищо от: `credentials.py`, `static/dist/`, `node_modules/`, `.pyc` файлове, dump-ове на базата или документи с лични данни.

### 5.3 Push и отваряне на pull request

```bash
git push -u origin feature/short-description
```

В GitHub натисни **Compare & pull request** (или Pull requests → New pull request), провери, че **base е `main`**, и опиши:

- **какво** се променя и **защо**;
- **как си го тествал** (тестове, страници, които си отворил);
- какво трябва да се направи на сървъра (напр. нов ключ в `credentials.py`).

### 5.4 Проверки

Трите проверки се пускат автоматично и се виждат най-долу в pull request-а.

- Червено ✗ → натисни **Details**, прочети грешката, оправи я локално, commit и пак `git push` — проверките се пускат отново.
- „This branch is out-of-date with the base branch“ → натисни **Update branch**. Ако има конфликти, обнови локално: `git switch main && git pull && git switch feature/short-description && git merge main`, разреши конфликтите, commit, `git push`.

### 5.5 Преглед и одобрение

1. Авторът: в pull request-а, **Reviewers** (дясната колона) → избери колега.
2. Проверяващият: отвори **Files changed**, коментирай редове с **+**, после **Review changes** → **Comment**, **Approve** или **Request changes** → **Submit review**.
3. Авторът: отговаря или оправя всеки коментар (новите commit-и обновяват pull request-а) и маркира разговорите като **Resolved**.

### 5.6 Merge и проверка на deploy-а

1. Когато всички проверки са зелени (и прегледът е готов), натисни **Merge pull request** → **Confirm merge**.
2. Отвори **Actions → Deploy to production** и изчакай изпълнението: трябва да завърши с **DEPLOYED … to https://aimtravel.bg**.
3. Отвори променените страници на https://aimtravel.bg.
4. Натисни **Delete branch** в pull request-а.

Ако deploy-ът се провали, обобщението казва на коя стъпка и дали нещо е променено — виж [точка 4.2](#42-какво-става-при-merge-на-pull-request) и [4.4](#44-отмяна-на-лоша-промяна).
