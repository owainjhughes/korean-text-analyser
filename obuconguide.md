# Sister-site brief: turning the Korean app into a SaeBae-shaped peer of ObuCon

This brief is written for a Claude session working **inside the Korean repo** (the FastAPI / Jinja2 app that serves `saebae.com`). It describes a project-level outline, not an implementation spec — the local Claude is expected to know the Korean codebase and pick its own libraries / file layout.

A peer site, **ObuCon** (`obucon.com`), exists for Japanese. The two apps are intentionally being shaped into a "matched pair": same idea (immersion-language readability + personal vocabulary tracking), same UX skeleton, same account model, different language and different tech stack underneath. The Korean app already has the hard part — tokenisation, analysis, and a dictionary — but it currently has no user accounts, no database, and a table-based output. This brief is about adding the missing skeleton and aligning the output, **not** rewriting what already works.

---

## What the Korean app is today

- FastAPI + Jinja2 templates.
- Tokenises Korean text and analyses it against levels 1–3 (no file upload).
- Has its own visual style already in place; that style stays.
- Already includes an analysis page and a dictionary page.
- **No** authentication, **no** user accounts, **no** database.

## What it needs to become

A Korean version of ObuCon, with the same shape:

- Logged-in users with a profile.
- A site-wide shell (navbar, language switcher, footer) so the app feels like a product rather than a single tool.
- The analysis page restyled into the richer ObuCon-style output (described below) instead of the current table.
- Eventually: per-user known/unknown vocabulary that the analysis page reads from. **This is explicitly out of scope for the first pass.**

The first pass is just **the UI shell + login/registration + profile**, layered onto what's already there. The existing analyser and dictionary keep working unchanged.

---

## What stays untouched

- The Korean tokeniser and any analysis logic behind it. Do not rework it.
- The existing dictionary feature and its data.
- The Korean site's existing visual style (colours, typography, branding, logo). Don't try to copy ObuCon's indigo `#55F` palette or its parrot logo — keep what's already there. The *structural* parity (navbar layout, page-to-page flow, auth-state behaviour) is what's being mirrored, not the *aesthetic*.

## What gets added

### 1. A site shell

A persistent navbar shown on every page, mirroring ObuCon's structure (without copying its visual treatment):

- Logo / brand on the left.
- Top-level nav links: **Home**, **Analysis**, **Dictionary**. (Vocabulary will join later — leave space for it but don't ship it yet.)
- A language-switcher pair on the right: a Korean-flag indicator marking "this site, current" and a Japanese-flag link out to `obucon.com`. (ObuCon already has the mirror of this, linking out to `saebae.com`.)
- When logged in: avatar / username dropdown with **Your profile** and **Sign out**.
- When logged out: **Login** and **Register** links/buttons.
- Mobile: hamburger menu collapsing the nav.

A simple footer is fine — match whatever the Korean app has now.

### 2. Pages

The page set, in priority order:

| Page | Route (suggested) | Auth | Notes |
|---|---|---|---|
| Home | `/` | protected | Landing for logged-in users; minimal content for the first pass — a welcome and links into Analysis / Dictionary. |
| Login | `/login` | public | Email + password. Redirects to Home on success. |
| Register | `/register` | public | Email + username + password. Same redirect. |
| Profile | `/profile` | protected | View / edit username + email; show account creation date. |
| Analysis | `/analysis` | protected | Existing functionality, restyled output (see "Analysis output" below). |
| Dictionary | `/dictionary` | protected | Existing functionality, fitted into the new shell. |
| Vocabulary | `/vocabulary` | protected | **Phase 2 only — do not build now.** |

"Protected" means: anonymous users hitting these routes are redirected to `/login`. Public pages remain reachable when logged out. Protection should be enforced server-side (the natural place in a FastAPI app); anything client-side is a convenience layer only.

### 3. Authentication

- Email + password registration and login.
- Sessions issued as an HTTP-only cookie containing a JWT (or equivalent signed token — the local Claude may pick the FastAPI-idiomatic option). Token validates the user on each request.
- Logout clears the cookie.
- Passwords stored as bcrypt hashes. **This format matters** — see the next section on shared accounts.
- Endpoints to expose, at minimum: register, login, logout, "who am I". The exact paths are the local Claude's call.

### 4. A database

The Korean app needs one. Postgres is the natural choice because that's what ObuCon uses, and shared accounts (the next section) require schema compatibility.

Minimum tables for the first pass:

- A `users` table with: id, email (unique), username (unique), bcrypt password hash, timestamps.

That's it for phase 1. No `known_words`, no analysis history yet.

---

## The shared-account question

Goal: one account works on both sites. A user who registers on ObuCon should be able to log in on SaeBae with the same credentials, and vice versa.

Because `obucon.com` and `saebae.com` are **different domains**, browsers cannot share the auth cookie between them. So "shared account" cannot mean "shared session" — it means **shared identity store**:

- Both apps read and write the **same `users` table** in the **same Postgres database**.
- Both apps use the same password hashing scheme (bcrypt) so a hash written by one verifies on the other.
- Each app issues its **own** session cookie scoped to its **own** domain. The user logs in on each site separately, but with the same email + password.

Implications for this first pass:

- The Korean app should be pointed at the **ObuCon Postgres** (the existing instance), not a fresh standalone DB. Talk to the user before committing to a DB endpoint — credentials and network reachability are environment-specific and the local Claude won't have them.
- If reaching the ObuCon DB is not yet feasible from the Korean app's environment, the **fallback** is: ship phase 1 against a separate local Postgres, but use **the same `users` schema** (column names, types, constraints) so a later cutover is a pure connection-string change, not a migration.
- Do **not** create a `users_korean` or otherwise duplicate the user identity. One identity, two sites.

The user has signalled that "same account" is preferred but that "if this causes big difficulties" we can step back. If the local Claude finds the cross-app DB sharing genuinely blocks progress (e.g., RDS isn't network-reachable from where the Korean app runs), pause and surface the constraint to the user rather than diverging the schema.

### What about other tables?

Tables that are clearly **per-language** (a Korean dictionary, future Korean known-word entries) can either:

- Live in the same DB as separate tables (`korean_dictionary`, etc.), or
- Re-use the existing `known_words` table, which is already language-scoped via a `language` column on the ObuCon side (values like `'ja'`, `'ko'`).

Lean toward the second option for `known_words` when that phase arrives — it's how the schema was designed. For the dictionary, a separate `korean_dictionary` table is fine since the Japanese one (`japanese_dictionary`) has language-specific columns (kanji, hiragana, JLPT) that don't apply.

This is **phase 2+ territory**. For phase 1, only `users` matters.

---

## Analysis output (the visual upgrade)

The Korean site currently shows its analysis as a table. ObuCon's analysis output is richer and is what the user wants reproduced — in Jinja, in the Korean app's existing visual style.

Concretely, the ObuCon analysis output has these elements (as a target description, not a template to copy verbatim):

- **A coverage summary at the top.** A big percentage representing "share of tokens the user already knows", plus a qualitative rating label (e.g. *Ineffective* / *Decent* / *Effective*) coloured by band. The thresholds ObuCon uses today: <75% ineffective (red), 75–85% decent (amber), 85–95% effective (green). The Korean side can use the same bands or pick its own — what matters is the *shape* of the summary.
- **A breakdown chart by level.** A pie or donut showing the distribution of tokens across the language's level system — in Korean's case, the existing levels 1–3, plus categories for "Unknown" and any other buckets the analyser already produces. Each band has a stable colour.
- **The text rendered as inline pills.** Every token shown as a coloured chip in reading order, where the colour encodes its level / known-status. Clicking or hovering reveals the token's meaning / lemma.
- **A "missing words" list.** All not-yet-known tokens listed below the text, each with a one-click "Mark as known" action — this hooks into the per-user vocabulary feature later. **For phase 1, the action button can be omitted or stubbed**; the *layout* is what's being established.

The point of doing this restyle in phase 1, even though the user-vocabulary feature lands later, is so the analysis page has the right shape from day one and only needs data wired in later, rather than a full UI rebuild.

This is to be implemented in **Jinja templates** in the Korean app's existing visual idiom — not as a React port. Charts can use whatever the Korean app already pulls in (or a small JS dep added for this purpose); the local Claude picks.

---

## Phasing

### Phase 1 — what this brief is asking for now

1. Add Postgres + a `users` table (schema-compatible with ObuCon's).
2. Add register / login / logout / "who am I" endpoints, JWT-in-cookie sessions, bcrypt hashes.
3. Add Login, Register, Profile pages.
4. Add a site-wide navbar + footer shell, including the JP/KR language switcher.
5. Wrap Home, Analysis, Dictionary in the new shell, and gate them behind login.
6. Restyle the Analysis output along the lines described above (without the "mark as known" wiring yet — it's a layout-only pass).

Phase 1 is done when: a new user can register, log in, see the navbar, visit Analysis and Dictionary as before (now restyled and behind auth), edit their profile, and log out — all on the Korean site, in its existing visual style.

### Phase 2 — later, separate brief

- Per-user known/unknown vocabulary, stored in a shared `known_words` table (language `'ko'`).
- "Mark as known" wiring on the analysis page.
- A `/vocabulary` page to list and manage known words.
- Connecting the Korean app to the shared ObuCon Postgres instance if phase 1 shipped against a local DB.

### Phase 3 — further out

- File / URL ingestion for analysis input, if desired.
- Cross-site flourishes (e.g. surfacing on the profile page that the same account also has a profile on the sister site).

---

## Non-goals for phase 1

- Don't migrate away from Jinja2.
- Don't rebuild the tokeniser or the analyser core.
- Don't import ObuCon's colour palette or logo — keep the Korean site's existing look.
- Don't build the vocabulary page or the "mark as known" backend.
- Don't try to share session cookies across the two domains. Identity is shared; sessions are not.

## When to stop and ask the user

- DB endpoint / credentials for the shared ObuCon Postgres — if the local Claude doesn't already know how to reach it, ask rather than guess.
- Whether to ship phase 1 against the shared DB or a local one (depends on the answer above).
- Anything that would require touching the existing tokeniser or analyser internals — that's out of scope and worth confirming before doing it.
- If the analysis-output restyle reveals that the existing analyser doesn't return enough information to render one of the elements above (e.g. per-token level data isn't exposed). Better to flag the gap than fake it.

---

## Reference: where the matching code lives in the ObuCon repo

For the local Claude's curiosity, the reference implementation on the Japanese side is in `software/` of the ObuCon dissertation repo:

- Backend: Go + Gin, `software/backend/internal/auth` (auth service, handler, JWT middleware) and `software/backend/internal/analysis` (analysis service / handler).
- Frontend: React + Tailwind, `software/frontend/src/pages/` (Login, Register, Profile, Analysis, Dictionary, Home) and `software/frontend/src/components/analysis/` (the rich analysis output the Korean side is being aligned with).
- Schema: `software/backend/migrations/001_init.up.sql` — particularly the `users` and `known_words` tables, which define the contract for shared accounts.

These are reference material only. Nothing in the Korean app should depend on the Go code; the brief is about parity of *shape*, not of *implementation*.
