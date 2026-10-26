# Frontend

The Next.js 16 user interface for the Text-to-SQL Data Analyst. Setup,
features and configuration are documented in the
[main README](../README.md); this page covers frontend-only work.

## Development

```bash
npm install
npm run dev        # http://localhost:3000, with hot reload
```

The app calls the backend at `http://localhost:8000` by default. To use another
URL, create `.env.local` here with `NEXT_PUBLIC_API_URL=...`. The value is
built into the bundle, so restart `npm run dev` (or rebuild) after changing it.

## Checks

```bash
npx tsc --noEmit   # type check
npm run lint       # ESLint
npm run build      # production build
```

There are no automated frontend tests yet.

## Where things live

| Path | Contents |
|---|---|
| `app/ChatInterface.tsx` | Page layout, chat input, sidebar panels, backend health check, pipeline toggle |
| `app/ChatMessage.tsx` | One answer: analysis, insights, follow-ups, SQL panel, export buttons, errors |
| `app/ChartRenderer.tsx` | Bar, line, pie and table rendering with Recharts |
| `app/api.ts` | Axios client and API types |
| `app/store.ts` | Zustand store for messages and saved queries |
| `app/components/` | Favorites, History, Analytics, Query Builder, CopyButton |
| `app/hooks/` | Dark mode, saved queries (favorites and history), message persistence, keyboard shortcuts |
| `app/utils/` | Error parsing and suggestions, CSV/JSON export |
| `app/globals.css` | Tailwind CSS, the class-based `dark:` variant, the `animate-pop` animation |

## Notes

- **Next.js 16** differs from older versions; read `AGENTS.md` and the docs
  bundled in `node_modules/next/dist/docs/` before relying on older patterns.
- **Dark mode:** Tailwind CSS 4 bases `dark:` on the operating-system setting by
  default. `globals.css` redefines it to follow the `.dark` class that
  `hooks/useDarkMode.ts` sets on `<html>`, so the in-app toggle works.
- **Docker:** the image builds the app itself (`npm ci` + `next build` with
  standalone output) and runs `node server.js`. `next.config.ts` enables
  standalone output only when `NEXT_STANDALONE=true`, so local `npm start`
  still works.
