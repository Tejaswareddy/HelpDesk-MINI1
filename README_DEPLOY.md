# Deploying HelpDesk Mini

This file explains two convenient deployment options so your frontend and admin work correctly.

Option A — Frontend-only on Vercel (quick, demo mode)

- The repo now includes a single-file frontend in `templates/index.html` that runs in demo mode when no backend is configured. Demo mode fakes login, ticket creation and comments so the UI is interactive for presentation.
- To deploy the standalone frontend on Vercel:
  1. Create a new Vercel project from the GitHub repository.
  2. In Vercel project settings, set the Framework Preset to "Other" and the output directory to `/templates` (or add a root-level `index.html` copy).
  3. Deploy. The site will be interactive using demo-mode automatically.

Option B — Frontend on Vercel, backend hosted elsewhere (recommended)

- Use this if you host the Django backend on Render, Railway, or another host. The frontend uses `window.__API_BASE__` when present, otherwise demo-mode.
- Set `vercel.json` rewrites to forward `/api/*` and `/admin/*` to your backend by editing `vercel.json`:

  Replace `https://YOUR_BACKEND.example.com` with your backend URL (for example: `https://helpdesk-api.fly.dev`).

  Example `vercel.json` (already included in repo):
  ```json
  {
    "rewrites": [
      { "source": "/api/(.*)", "destination": "https://your-backend.example.com/api/$1" },
      { "source": "/admin/:path*", "destination": "https://your-backend.example.com/admin/:path*" },
      { "source": "/(.*)", "destination": "/index.html" }
    ]
  }
  ```

  Steps:
  1. Deploy your Django backend (Render/Railway/Heroku). Note the base URL where it’s reachable.
  2. Update `vercel.json` with that URL and push.
  3. Create a Vercel project from the repo and deploy. Requests to `/api` and `/admin` will be proxied to your backend.

Option C — Host both frontend and backend together

- Deploy the Django app (with templates) to a Python host (Render, Railway). Configure static files with WhiteNoise and run `python manage.py collectstatic` before or during deploy.

Environment variables & production notes
- When you switch to a real backend, set `DEBUG=False`, set `ALLOWED_HOSTS` in Django settings, and provide `SECRET_KEY` and DB credentials as environment variables.
- For CORS cross-origin setups, install and configure `django-cors-headers`.

If you want, I can:
- Replace `YOUR_BACKEND.example.com` in `vercel.json` with your real backend URL and push the change.
- Add a small `index.html` copy to repo root (if Vercel needs it in project root).
