# Opt-in hosted synthetic training demo — security boundary

**Not a production deployment and not suitable for real company data.** Remote mode allows the *fictional* training case to be tested over a HTTPS-hosted website. It does not implement enterprise IAM, multi-tenancy, durable storage or regulatory authorization. Never give your real confidential Zetaris/warehouse connection to a public hackathon demo.

## Deployment settings (Render-style Docker hosting, manual setup)

1. Create a **private** repo first; remove all `.env`, `*.db`, credentials and real inventory. Push the project contents with `Dockerfile` at the root. Confirm the provider has Docker-based Python web service support and HTTPS. There is no guarantee a free tier or persistence is available.
2. In the host's **private environment variable** settings, set:

   | Variable | Value |
   | --- | --- |
   | `FOODRECALL_DEMO_REMOTE` | `1` |
   | `FOODRECALL_PUBLIC_ORIGIN` | exact `https://YOUR-HOSTNAME` (no final `/`, no path) |
   | `FOODRECALL_BOOTSTRAP_PASSWORD` | long, private random secret 16+ characters |
   | `FOODRECALL_ANALYST_PASSWORD` | a DIFFERENT private random secret 16+ characters |
   | `FOODRECALL_DB` | writable on-disk path (`/tmp/foodrecall-training.sqlite` for ephemeral demo only) |
   | `PORT` | host-assigned port; Dockerfile accepts it automatically |

3. The host must terminate TLS correctly. Cookies are `Secure`, `HttpOnly`, `SameSite=Strict`; direct HTTP auth may not work (by design). Verify the exact host URL, sign-in, `/api/cases` anonymous => 401, signed-in => 200, wrong `Origin` => 403, logout => revoked and safe demo workflow with an unshared test account.
4. Treat an ephemeral filesystem as **resetting your demo database** when the service restarts. A new startup seeds fictional records and creates users using the provided secrets. Persistent volume/DB and disaster recovery are separate production projects, not claims of this demo.
5. Do not put any provider API keys into GitHub or public client Javascript. Never call real warehouse APIs from this demo. Monitor usage/cost/quotas and disable if compromised.

## Why production remains blocked

Single-org training RBAC, 8-hour cookie sessions and CSRF are *not* a substitute for a security audit, rate-limited public authentication infrastructure, per-tenant data isolation, enterprise IAM, approved data processors, monitoring and durable backups. Food safety workflows require a qualified reviewer. A public demo URL only demonstrates a fictional workflow, not a live FDA-to-company-inventory match.

## Default safe state

`FOODRECALL_DEMO_REMOTE=0` or unset means non-loopback callers cannot read private API endpoints. Starting the container with `0.0.0.0` does not by itself expose API data. If remote mode is `1` but HTTPS origin or strong passwords are missing, the app **refuses startup**. Do not bypass this validation.
