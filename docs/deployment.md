# GitHub → Vercel frontend + DigitalOcean API

One-time connection and environment setup are required. Afterward, the supplied configurations support deployment on pushes to `main`.

## 1. Publish the repository

The local repository is initialized on `main`. Create/select your GitHub repository, then:

```sh
git add .
git status
git commit -m "Build weather-aware truck routing assessment"
git remote add origin https://github.com/YOUR_OWNER/YOUR_REPOSITORY.git
git push -u origin main
```

Before publishing, `git check-ignore backend/.env env.txt` must list both paths. The repository includes the supplied assessment PDF; remove it from the submission if redistribution is not appropriate. No real secrets belong in `.do/app.yaml`.

GitHub Actions runs Python checks, frontend tests, TypeScript/production build, and browser tests. CI uses deterministic provider fixtures and needs no API keys.

## 2. Deploy the Django API on DigitalOcean

Expected entry-level cost: **from $5/month**, subject to the configuration shown in the account. Promotional credits were not verified; see [provider research](providers.md). This step creates paid infrastructure and should be done only after accepting that cost.

1. In App Platform, connect GitHub and select this repository / `main`.
2. Import `.do/app.yaml` (replace `REPLACE_OWNER/REPLACE_REPOSITORY`) or configure a service with source directory `backend` and Dockerfile `backend/Dockerfile` relative to the repository.
3. Select a service plan you approve. The template requests `basic-xxs`, one instance, NYC region. Confirm that slug/price in the current account; the spec has not been applied to a live account.
4. Configure runtime secrets: `DJANGO_SECRET_KEY` (random, at least 32 characters), `ORS_API_KEY`, `GEOAPIFY_API_KEY`. Replace every `REPLACE_*` value before deployment.
5. Set `ENVIRONMENT=production`, `DEBUG=false`, `ALLOWED_HOSTS` to the assigned backend hostname (no scheme), and `CORS_ALLOWED_ORIGINS` to the exact frontend HTTPS origin.
6. Port: 8080. Health check: `/api/health/`. The container runs Gunicorn as a non-root user, with one process/four threads and a 180-second request timeout. No migrations or database are required.
7. Enable auto-deploy on push. Verify `https://YOUR_API_HOST/api/health/` returns `{"status":"ok"}`.

Generate a Django secret locally with `python -c "import secrets; print(secrets.token_urlsafe(48))"`, then paste it only into the platform's secret field. The production settings deliberately reject the development secret. The `.env` file is excluded from Docker images; the platform injects configuration.

## 3. Deploy the frontend on Vercel

1. Import the same GitHub repository.
2. Keep **Root Directory = repository root**. Root `vercel.json` supplies installation/build/output settings. This avoids needing a second repository or manually moving files.
3. Set `VITE_API_BASE_URL=https://YOUR_API_HOST` for the intended deployment environments. No trailing `/api`; the client adds it.
4. Optional: `VITE_MAP_STYLE_URL` for another licensed MapLibre style. Default OpenFreeMap does not require credentials.
5. Deploy. Add the resulting exact frontend origin to DigitalOcean's `CORS_ALLOWED_ORIGINS` and redeploy the API if necessary.
6. Subsequent `main` pushes redeploy production; branch pushes can produce Vercel previews. Preview hosts need explicit CORS configuration if used for live API tests. Do not open CORS to every origin just to make previews work.

`VITE_*` variables are build-time/public. Never put ORS, Geoapify server credentials, or Django secrets there. No browser routing keys are needed. The app has one entry page and no client-side nested routes, so no catch-all rewrite is necessary; assets and the recorded demo are served directly.

## 4. Verify the deployment

- Health endpoint returns 200 over HTTPS.
- Enter Chicago, Illinois → Merrillville, Indiana, future departure, 35,000 lb, 10-mile spacing.
- Confirm genuine alternatives and no provider warning (actual availability may change).
- Inspect checkpoint ETAs and unit labels; switch routes.
- Scrub to +48h and check there is no additional `/api/routes/analyze/` request.
- Try Chicago → Indianapolis and confirm fewer-route messaging if only two alternatives exist.
- Test a blocked/missing-data fixture using the automated suite; never falsify a live forecast for demonstration.
- Check browser console, API logs and CORS. Check the map worker URL returns JavaScript in production.

## Operational constraints

The default cache/throttle store is per process. Keep one process/instance for this assessment configuration; use Redis or another shared Django cache before scaling. Address search is 60 requests/minute/IP and route analysis 6/minute/IP. Canceled browser requests may still finish at the provider and consume quota. Provider caches expire after 15 minutes. Update the recorded demo deliberately using the supplied scripts, never as an automatic live-error fallback.

Docker and remote platform deployment were not executed in this environment. Local production frontend builds and Django configuration checks were executed. Account connection, repository ownership, production URLs, paid-service approval, and final remote smoke tests remain submission steps.
