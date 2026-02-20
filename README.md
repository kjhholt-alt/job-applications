# Job Applications

Organized system for tailored job applications. Each application gets its own folder with a resume, cover letter, and job description tailored to that specific role.

## Folder Structure

```
job-applications/
  templates/
    base-resume.md          # Master resume with ALL experience (source of truth)
  applications/
    <company-role-name>/
      job-description.md    # Saved job posting + metadata (date applied, source, etc.)
      resume.md             # Tailored resume for this specific role
      cover-letter.md       # Tailored cover letter
  cover-letters/            # Standalone cover letter templates (if needed)
```

## How to Use for a New Application

1. **Save the job description** to `applications/<company-role>/job-description.md`
2. **Copy the base resume** from `templates/base-resume.md`
3. **Tailor the resume**: Reorder sections, pick relevant bullets, match keywords from the JD
4. **Write the cover letter**: Address specific requirements, explain fit, handle any gaps
5. **Export to PDF**: Copy the markdown into Google Docs / Word and format, or use a markdown-to-PDF tool

## Job Similarity Finder (Streamlit)

Lightweight job matcher that compares new jobs to your liked set using Claude-powered fingerprints.

**Folders**
- `jobs/inbox/` drop new job descriptions here (markdown)
- `jobs/liked/` drop jobs you like here (markdown)
- `data/jobs.db` local index
 - `data/interest_profile.json` saved preferences

**Run**
```powershell
cd C:\Users\Kruz\Desktop\Projects\job-applications
pip install -r requirements.txt
streamlit run app.py
```

**Optional login (recommended for hosted use)**
Set any of these env vars to require a login:
- `APP_USER` + `APP_PASS`
- `APP_USER1` + `APP_PASS1`, `APP_USER2` + `APP_PASS2` (up to 3 pairs)
- `APP_USERS_JSON` = `[{"username": "...", "password": "..."}]`
If you want per-user data isolation (hosted), set:
- `APP_USER_STORAGE=per_user`

Example `.env.local`:
```
APP_USER1=kruz
APP_PASS1=your_password
APP_USER2=friend
APP_PASS2=friend_password
APP_USER_STORAGE=per_user
```

**Base resume for hosted use**
- Upload a markdown resume in the Profile tab (stored per user).
- If none is uploaded, the app falls back to `templates/base-resume.example.md`.

**Workflow**
1. Add liked jobs to `jobs/liked/`, then click `Ingest Liked`.
2. Add new jobs to `jobs/inbox/`, then click `Ingest Inbox`.
3. Review matches and move the best ones to liked.
4. Generate tailored `resume.md` + `cover-letter.md` directly into `applications/<company-role>/`.
5. Configure your Interest Profile and alert feeds in the `Profile` tab.

**Job Description Format (optional but recommended)**
```md
---
id: deloitte-finance-ai-manager
company: Deloitte
role: Finance Analytics & AI Manager
location: Chicago, IL (Hybrid)
level: Manager
domain: Finance Transformation
skills: [finance, analytics, ai, powerbi, sql, python, consulting]
source: LinkedIn
date_saved: 2026-02-20
liked: true
---
<job description text>
```

## Auto-Import Applied Jobs

Use the `Ingest` tab button to copy `applications/*/job-description.md` into `jobs/liked/`.

## Job Alerts

Add RSS/feed URLs in the `Profile` tab, then click `Run Alerts Now` to drop new items into `jobs/inbox/`.

## Scheduled Alerts (Windows Task Scheduler)

Use the helper script to create an hourly task:
```powershell
cd C:\Users\Kruz\Desktop\Projects\job-applications
powershell -ExecutionPolicy Bypass -File .\scripts\register_task.ps1
```

Manual run:
```powershell
cd C:\Users\Kruz\Desktop\Projects\job-applications
powershell -ExecutionPolicy Bypass -File .\scripts\run_alerts.ps1
```

### Quick Claude Prompt for Future Tailoring

> "I have a job application in `job-applications/applications/<folder>/`. Read the job-description.md and my base resume in templates/base-resume.md. Create a tailored resume.md and cover-letter.md for this role. Highlight my GenAI projects and finance experience."

## Applications Tracker

| Date | Company | Role | Status | Folder |
|------|---------|------|--------|--------|
| 2026-02-20 | Deloitte | Finance Analytics & AI Manager | Applied | `deloitte-finance-ai-manager/` |
| 2026-02-20 | Deloitte | AI Solutions Leader (HC) | Applied | `deloitte-ai-solutions-leader/` |

## Resume Strategy Notes

- **Finance + AI builder** is the unique angle. Most finance people can't code. Most coders don't know finance. You do both.
- **Personal projects are production work** — frame them as real applications with real users, not hobby projects
- Lead with whichever section (finance or tech) is more relevant to the specific role
- Always address the STEM degree gap directly in cover letters — your project portfolio demonstrates technical capability
- Quantify wherever possible: dollar amounts, user counts, performance improvements, cycle time reductions
