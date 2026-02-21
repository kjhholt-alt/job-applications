import json
import os
from pathlib import Path

import streamlit as st

from job_finder.auth import require_login


def _split_list(value: str):
    return [v.strip().lower() for v in value.split(",") if v.strip()]


def _configure_user_workspace(user: str | None) -> None:
    storage_mode = (os.environ.get("APP_USER_STORAGE") or "").strip().lower()
    if storage_mode != "per_user" or not user:
        return
    base_dir = Path(__file__).resolve().parent
    user_root = base_dir / "data" / "users" / user
    os.environ["JOB_FINDER_DATA_ROOT"] = str(user_root)


st.set_page_config(page_title="Job Similarity Finder", layout="wide")
current_user = require_login()
_configure_user_workspace(current_user)

from job_finder.alerts import build_alert_email, run_alerts, send_resend_email
from job_finder.app_logic import (
    auto_import_applications_to_liked,
    bulk_generate_applications,
    create_application_folder,
    ingest_folder,
    list_inbox_files,
    list_liked_files,
    load_base_resume,
    move_to_liked,
)
from job_finder.claude import ClaudeClient
from job_finder.config import (
    get_applications_dir,
    get_data_dir,
    get_inbox_dir,
    get_liked_dir,
    get_user_base_resume_path,
    get_user_templates_dir,
    INBOX_DIR,
    LIKED_DIR,
)
from job_finder.env import ensure_anthropic_key, ensure_resend_key, get_resend_from
from job_finder.filtering import evaluate_filters, load_reputable_companies, save_reputable_companies
from job_finder.profile import InterestProfile, load_profile, save_profile
from job_finder.scoring import score_against_liked
from job_finder.scraper import extract_search_terms, scrape_similar_jobs, save_jobs_to_inbox
from job_finder.storage import list_jobs, upsert_job

st.title("Job Application Assistant")
st.caption("Generate tailored resumes and cover letters for jobs similar to ones you've already applied to.")

for folder in [
    get_data_dir(),
    get_inbox_dir(),
    get_liked_dir(),
    get_applications_dir(),
    get_user_templates_dir(),
]:
    folder.mkdir(parents=True, exist_ok=True)

# ── Setup checklist ────────────────────────────────────────────────────────
base_resume_exists = load_base_resume() != ""
liked_jobs_count = len(list_jobs("liked"))
inbox_jobs_count = len(list_jobs("inbox"))
liked_with_fp = sum(1 for j in list_jobs("liked") if j.fingerprint_json)
inbox_with_fp = sum(1 for j in list_jobs("inbox") if j.fingerprint_json)

all_ready = base_resume_exists and liked_with_fp > 0 and inbox_with_fp > 0

with st.expander("How this works — setup checklist" if not all_ready else "✅ Setup complete — ready to generate", expanded=not all_ready):
    st.markdown("### How it works")
    st.markdown(
        "This tool learns what jobs you like based on roles you've already applied to, "
        "then finds similar jobs from your inbox and generates a **tailored resume + cover letter for each one** automatically."
    )

    st.markdown("### Setup checklist")

    # Step 1
    if base_resume_exists:
        st.success("**Step 1 — Base resume:** Loaded ✓")
    else:
        st.error("**Step 1 — Base resume: Missing ✗**")
        st.markdown(
            "Go to the **Profile** tab → upload your resume as a `.md` or `.txt` file. "
            "This is the source of truth — Claude will tailor it to each job without inventing anything."
        )

    # Step 2
    if liked_with_fp > 0:
        st.success(f"**Step 2 — Applied jobs ingested:** {liked_with_fp} job(s) with fingerprints ✓")
    elif liked_jobs_count > 0:
        st.warning(f"**Step 2 — Applied jobs:** {liked_jobs_count} imported but not yet fingerprinted")
        st.markdown("Go to **Ingest** tab → click **Ingest Liked** (make sure 'Run Claude fingerprint extraction' is checked).")
    else:
        st.error("**Step 2 — Applied jobs: None imported ✗**")
        st.markdown(
            "Go to the **Ingest** tab → click **'Copy applications/ job descriptions into liked bucket'** "
            "→ then click **Ingest Liked**. "
            "This tells the system what kinds of roles you're targeting."
        )

    # Step 3
    if inbox_with_fp > 0:
        st.success(f"**Step 3 — New jobs to apply to:** {inbox_with_fp} job(s) ready ✓")
    elif inbox_jobs_count > 0:
        st.warning(f"**Step 3 — Inbox jobs:** {inbox_jobs_count} loaded but not fingerprinted")
        st.markdown("Go to **Ingest** tab → click **Ingest Inbox**.")
    else:
        st.error("**Step 3 — Inbox jobs: Empty ✗**")
        st.markdown("---")
        st.markdown("#### How to add jobs to your inbox")
        st.markdown(
            "These are jobs you **want to apply to** — the system will find the ones most similar "
            "to your Deloitte applications and generate a tailored resume + cover letter for each."
        )
        st.markdown("**Here's how to add them:**")
        st.markdown(
            "1. Find a job posting on LinkedIn, Indeed, or a company careers page\n"
            "2. Copy the full job description text\n"
            "3. Paste it into a new file — name it something like `company-role.md` (e.g. `pwc-ai-manager.md`)\n"
            f"4. Save that file into this folder on your computer:\n\n   `{get_inbox_dir()}`\n\n"
            "5. Repeat for as many jobs as you want (aim for 10–20)\n"
            "6. Come back here and go to **Ingest** tab → click **Ingest Inbox**"
        )
        st.info("💡 No special formatting needed — just paste the raw job description text and save as .md")

    # Step 4
    if all_ready:
        st.success("**Step 4 — Generate:** Go to the **Bulk Generate** tab, pick a seed job, and hit generate.")
    else:
        st.info("**Step 4 — Generate:** Once steps 1–3 are done, go to **Bulk Generate** to create your documents.")

api_key, key_source = ensure_anthropic_key()
resend_key, resend_source = ensure_resend_key()
resend_from = get_resend_from()

with st.sidebar:
    dark_mode = st.toggle("Dark mode", value=False)

if dark_mode:
    st.markdown(
        """
        <style>
        .stApp { background-color: #0f1115; color: #e6e6e6; }
        [data-testid="stSidebar"] { background-color: #12151c; }
        .stTextInput input, .stTextArea textarea, .stSelectbox div, .stMultiSelect div {
            background-color: #161a22 !important;
            color: #e6e6e6 !important;
        }
        .stButton button {
            background-color: #1f2430 !important;
            color: #e6e6e6 !important;
            border: 1px solid #2a3140 !important;
        }
        .stMarkdown, .stCaption, .stTextInput label, .stTextArea label, .stSelectbox label {
            color: #e6e6e6 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

with st.sidebar:
    st.header("Workspace")
    current_root = str(Path(get_inbox_dir()).parents[1])
    workspace_input = st.text_input("Workspace root", value=current_root)
    if st.button("Set Workspace Root (restart required)"):
        env_path = Path(current_root) / ".env.local"
        lines = []
        if env_path.exists():
            lines = env_path.read_text(encoding="utf-8").splitlines()
        lines = [l for l in lines if not l.startswith("WORKSPACE_ROOT=")]
        lines.append(f"WORKSPACE_ROOT={workspace_input}")
        env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        st.success("Saved WORKSPACE_ROOT to .env.local. Restart the app.")

    st.header("Claude Status")
    if api_key:
        st.success("Anthropic key loaded")
        if key_source:
            st.caption(f"Source: {key_source}")
    else:
        st.error("No Anthropic key found")
        st.caption("Add ANTHROPIC_API_KEY to a .env or set an env var.")

    st.header("Resend Status")
    if resend_key:
        st.success("Resend key loaded")
        if resend_source:
            st.caption(f"Source: {resend_source}")
    else:
        st.warning("No Resend key found")

    if resend_from:
        st.caption(f"From: {resend_from}")

    st.header("Buckets")
    st.caption(f"Inbox: {get_inbox_dir()}")
    st.caption(f"Liked: {get_liked_dir()}")

client = ClaudeClient(api_key) if api_key else None
profile = load_profile()


tab_ingest, tab_matches, tab_liked, tab_profile, tab_bulk = st.tabs(["Ingest", "Matches", "Liked", "Profile", "Bulk Generate"])

with tab_ingest:
    st.info(
        "**This tab feeds the system.** "
        "First import your already-applied jobs (Liked), then add new jobs you want docs for (Inbox). "
        "Fingerprinting uses Claude to extract skills/keywords from each job — required before scoring or generating."
    )
    st.subheader("Step 1 — Import your applied jobs (Liked)")
    st.caption("Pulls job-description.md from each folder in applications/ into the liked bucket.")
    if st.button("Copy applications/ job descriptions into liked bucket"):
        count = auto_import_applications_to_liked()
        st.success(f"Copied {count} file(s) to jobs/liked/")

    st.divider()
    st.subheader("Step 2 — Run fingerprinting on Liked jobs")
    st.caption("Extracts skills, domains, and keywords from each liked job. This is what similarity scoring is based on.")

    st.subheader("Liked Jobs")
    inbox_files = list_inbox_files()
    if not inbox_files:
        st.info("Drop job-description markdown files into jobs/inbox/")
    else:
        for path in inbox_files:
            st.write(path.name)

    st.divider()
    st.subheader("Step 3 — Find Similar Jobs Automatically")

    liked_for_scrape = list_jobs("liked")
    liked_fps_for_scrape = []
    for j in liked_for_scrape:
        if j.fingerprint_json:
            try:
                liked_fps_for_scrape.append(json.loads(j.fingerprint_json))
            except Exception:
                pass

    if liked_fps_for_scrape:
        terms_preview = extract_search_terms(liked_fps_for_scrape)
        st.markdown(
            "Based on your applied jobs, we'll search LinkedIn for similar roles and drop them "
            "straight into your inbox — ready to fingerprint and generate documents for."
        )
        st.caption(f"Search terms derived from your profile: **{' | '.join(terms_preview)}**")

        col_loc, col_n = st.columns(2)
        with col_loc:
            scrape_location = st.text_input("Location", value="United States")
        with col_n:
            scrape_n = st.number_input("Results per search term", min_value=5, max_value=30, value=15, step=5)

        if st.button("🔍 Find Similar Jobs on LinkedIn", type="primary"):
            scrape_status = st.empty()
            scrape_progress = st.progress(0)

            scraped_jobs = []
            scrape_errors = []

            def _scrape_progress(step, total, msg):
                scrape_status.text(msg)
                scrape_progress.progress((step + 1) / max(total, 1))

            try:
                scraped_jobs = scrape_similar_jobs(
                    fingerprints=liked_fps_for_scrape,
                    location=scrape_location,
                    results_per_term=int(scrape_n),
                    on_progress=_scrape_progress,
                )
            except Exception as e:
                scrape_errors.append(str(e))

            scrape_progress.progress(1.0)

            if scrape_errors:
                scrape_status.text("Finished with errors.")
                for err in scrape_errors:
                    st.error(err)
            elif not scraped_jobs:
                scrape_status.text("No jobs found — LinkedIn may be rate limiting. Try again in a minute.")
            else:
                saved_paths = save_jobs_to_inbox(scraped_jobs, get_inbox_dir())
                scrape_status.text(f"Saved {len(saved_paths)} job(s) to inbox.")
                st.success(f"Found **{len(scraped_jobs)} jobs** across {len(terms_preview)} searches → saved to inbox. Now click **Ingest Inbox** below.")
                for j in scraped_jobs:
                    st.write(f"• **{j['company']}** — {j['title']} ({j['location']})")
    else:
        st.info("Complete Step 2 first — ingest your applied jobs so we know what to search for.")

    st.divider()
    st.subheader("Step 3b — Or add jobs manually")
    st.markdown(
        f"Drop job description `.md` files into:\n\n`{get_inbox_dir()}`\n\n"
        "Then ingest them below."
    )

    run_fingerprint = st.checkbox("Run Claude fingerprint extraction", value=True)
    if st.button("Ingest Inbox"):
        if run_fingerprint and not client:
            st.error("Claude key missing")
        else:
            ingested = ingest_folder(INBOX_DIR, "inbox", client if run_fingerprint else None)
            st.success(f"Ingested {len(ingested)} job(s)")

    st.divider()
    st.subheader("Liked Jobs")
    liked_files = list_liked_files()
    if not liked_files:
        st.info("Drop liked job markdown files into jobs/liked/")
    else:
        for path in liked_files:
            st.write(path.name)

    if st.button("Ingest Liked"):
        if run_fingerprint and not client:
            st.error("Claude key missing")
        else:
            ingested = ingest_folder(LIKED_DIR, "liked", client if run_fingerprint else None)
            st.success(f"Ingested {len(ingested)} liked job(s)")

    st.subheader("Job Alerts")
    st.caption("Runs RSS/feeds configured in Profile and drops new items into inbox")
    if st.button("Run Alerts Now"):
        current_profile = load_profile()
        new_files = run_alerts(current_profile)
        st.success(f"Added {len(new_files)} new job(s) to inbox")
        if current_profile.alert_email_enabled and current_profile.alert_email_to and resend_key and new_files:
            html = build_alert_email(new_files)
            send_resend_email(
                resend_key,
                current_profile.alert_email_to,
                "Job Finder Alerts",
                html,
                from_email=resend_from,
            )
            st.success("Alert email sent")

with tab_liked:
    st.subheader("Liked Library")
    liked_jobs = list_jobs("liked")
    if not liked_jobs:
        st.info("No liked jobs in DB. Ingest jobs/liked/ first.")
    else:
        for job in liked_jobs:
            st.markdown(f"**{job.company or 'Unknown'} — {job.role or job.job_id}**")
            st.caption(job.path)
            if job.fingerprint_json:
                st.caption("Fingerprint ready")
            else:
                if st.button(f"Create fingerprint for {job.job_id}"):
                    if not client:
                        st.error("Claude key missing")
                    else:
                        fingerprint = client.extract_fingerprint(job.body)
                        upsert_job({
                            "job_id": job.job_id,
                            "path": job.path,
                            "bucket": job.bucket,
                            "liked": job.liked,
                            "company": job.company,
                            "role": job.role,
                            "location": job.location,
                            "level": job.level,
                            "domain": job.domain,
                            "skills": job.skills,
                            "source": job.source,
                            "date_saved": job.date_saved,
                            "body": job.body,
                            "fingerprint": fingerprint,
                        })
                        st.success("Fingerprint added")
            st.divider()

with tab_matches:
    st.subheader("Top Matches")
    inbox_jobs = list_jobs("inbox")
    liked_jobs = list_jobs("liked")

    liked_fps = []
    for job in liked_jobs:
        if job.fingerprint_json:
            try:
                liked_fps.append(json.loads(job.fingerprint_json))
            except json.JSONDecodeError:
                pass

    if not inbox_jobs:
        st.info("No inbox jobs in DB. Ingest jobs/inbox/ first.")
    elif not liked_fps:
        st.warning("No liked fingerprints available. Ingest liked jobs with fingerprints.")
    else:
        scored = []
        for job in inbox_jobs:
            if not job.fingerprint_json:
                score = 0.0
            else:
                try:
                    job_fp = json.loads(job.fingerprint_json)
                except json.JSONDecodeError:
                    job_fp = {}
                score = score_against_liked(job_fp, liked_fps, profile)
            scored.append((score, job))

        scored.sort(key=lambda x: x[0], reverse=True)

        for score, job in scored:
            job_fp = {}
            if job.fingerprint_json:
                try:
                    job_fp = json.loads(job.fingerprint_json)
                except json.JSONDecodeError:
                    job_fp = {}
            filters = evaluate_filters(job.body or "", job.company, job_fp, profile)

            st.markdown(f"**{job.company or 'Unknown'} — {job.role or job.job_id}**")
            if filters.salary_unknown:
                st.caption(f"Match score: {score}  •  Salary: unknown (low priority)")
            elif filters.salary_value:
                st.caption(f"Match score: {score}  •  Salary: ${filters.salary_value:,}")
            else:
                st.caption(f"Match score: {score}")
            st.caption(job.path)
            if filters.notes:
                st.caption("Flags: " + ", ".join(filters.notes))

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"Move to Liked: {job.job_id}"):
                    moved = move_to_liked(job)
                    st.success(f"Moved to liked: {moved}")
            with col2:
                if st.button(f"Generate Resume+CL: {job.job_id}"):
                    if not client:
                        st.error("Claude key missing")
                    else:
                        base_resume = load_base_resume()
                        if not base_resume:
                            st.error("Missing templates/base-resume.md")
                        else:
                            resume_md, cover_md = client.generate_tailored_docs(base_resume, job.body)
                            dest = create_application_folder(job, resume_md, cover_md)
                            st.success(f"Created application folder: {dest}")
            with col3:
                if st.button(f"Fingerprint: {job.job_id}"):
                    if not client:
                        st.error("Claude key missing")
                    else:
                        fingerprint = client.extract_fingerprint(job.body)
                        upsert_job({
                            "job_id": job.job_id,
                            "path": job.path,
                            "bucket": job.bucket,
                            "liked": job.liked,
                            "company": job.company,
                            "role": job.role,
                            "location": job.location,
                            "level": job.level,
                            "domain": job.domain,
                            "skills": job.skills,
                            "source": job.source,
                            "date_saved": job.date_saved,
                            "body": job.body,
                            "fingerprint": fingerprint,
                        })
                        st.success("Fingerprint updated")
            st.divider()

with tab_bulk:
    st.subheader("Bulk Generate — Resumes & Cover Letters")
    st.markdown(
        "Pick a job you've already applied to as the **seed**. "
        "We'll find the most similar inbox jobs and generate a tailored resume + cover letter for each one."
    )

    liked_jobs_all = list_jobs("liked")
    liked_with_fp = [j for j in liked_jobs_all if j.fingerprint_json]

    if not liked_with_fp:
        st.warning(
            "No liked jobs with fingerprints found. "
            "Go to **Ingest** → copy your applied jobs → run **Ingest Liked** with fingerprinting enabled."
        )
    else:
        seed_options = {
            f"{j.company or 'Unknown'} — {j.role or j.job_id}": j
            for j in liked_with_fp
        }
        selected_label = st.selectbox("Seed job (your applied / liked job)", list(seed_options.keys()))
        seed_job = seed_options[selected_label]

        inbox_jobs_all = list_jobs("inbox")
        inbox_with_fp = [j for j in inbox_jobs_all if j.fingerprint_json]

        col_a, col_b = st.columns(2)
        with col_a:
            top_n = st.number_input(
                "How many similar jobs to generate docs for",
                min_value=1, max_value=20, value=10, step=1,
            )
        with col_b:
            st.metric("Inbox jobs available", len(inbox_with_fp))

        if inbox_with_fp:
            # Preview: show top matches before generating
            if st.button("Preview Top Matches (no generation)"):
                import json as _json
                from job_finder.scoring import rank_by_seed as _rank

                pairs = []
                for j in inbox_with_fp:
                    try:
                        pairs.append((j, _json.loads(j.fingerprint_json)))
                    except Exception:
                        pass

                seed_fp = _json.loads(seed_job.fingerprint_json)
                ranked = _rank(pairs, seed_fp, top_n=int(top_n))

                st.markdown(f"**Top {len(ranked)} matches for:** {selected_label}")
                for rank_i, (score, job) in enumerate(ranked, 1):
                    st.write(f"{rank_i}. **{job.company or 'Unknown'} — {job.role or job.job_id}** — score: `{score:.3f}`")

        st.divider()

        if st.button(f"Generate {int(top_n)} Resumes + Cover Letters", type="primary"):
            if not client:
                st.error("Claude key missing — add ANTHROPIC_API_KEY.")
            else:
                base_resume = load_base_resume()
                if not base_resume:
                    st.error("Missing base resume. Upload one in the Profile tab.")
                elif not inbox_with_fp:
                    st.warning("No inbox jobs with fingerprints. Ingest inbox first.")
                else:
                    status_text = st.empty()
                    progress_bar = st.progress(0)

                    generated_results = []
                    total_jobs = min(int(top_n), len(inbox_with_fp))

                    def _on_progress(i, total, job):
                        label = f"{job.company or 'Unknown'} — {job.role or job.job_id}"
                        status_text.text(f"Generating {i + 1}/{total}: {label}…")
                        progress_bar.progress((i + 1) / total)

                    try:
                        generated_results = bulk_generate_applications(
                            seed_job=seed_job,
                            inbox_jobs=inbox_with_fp,
                            base_resume=base_resume,
                            client=client,
                            top_n=int(top_n),
                            on_progress=_on_progress,
                        )
                    except ValueError as e:
                        st.error(str(e))

                    progress_bar.progress(1.0)
                    status_text.text("Done.")

                    if generated_results:
                        successes = [r for r in generated_results if r["error"] is None]
                        failures = [r for r in generated_results if r["error"] is not None]

                        st.success(f"Generated {len(successes)} application(s) successfully.")

                        for r in successes:
                            job = r["job"]
                            label = f"{job.company or 'Unknown'} — {job.role or job.job_id}"
                            st.markdown(
                                f"✅ **{label}** — similarity `{r['score']:.3f}` — `{r['folder']}`"
                            )

                        for r in failures:
                            job = r["job"]
                            label = f"{job.company or 'Unknown'} — {job.role or job.job_id}"
                            st.error(f"❌ {label} — {r['error']}")


with tab_profile:
    st.info(
        "**Start here.** Upload your base resume before doing anything else. "
        "Claude uses it as the source of truth when tailoring documents — it will never invent jobs, dates, or credentials."
    )

    st.subheader("Base Resume")
    st.caption("Upload your resume as a markdown (.md) or plain text (.txt) file. Paste it into a .md file if needed.")
    user_resume_path = get_user_base_resume_path()
    if user_resume_path.exists():
        st.caption(f"Loaded: {user_resume_path}")
    else:
        st.caption("No user resume found. Upload one below.")
    uploaded_resume = st.file_uploader("Upload base resume (markdown)", type=["md", "txt"])
    if uploaded_resume and st.button("Save Base Resume"):
        content = uploaded_resume.getvalue().decode("utf-8", errors="ignore")
        user_resume_path.write_text(content, encoding="utf-8")
        st.success("Base resume saved")

    focus_skills = st.text_input("Focus skills (comma-separated)", ", ".join(profile.focus_skills))
    focus_domains = st.text_input("Focus domains (comma-separated)", ", ".join(profile.focus_domains))
    focus_keywords = st.text_input("Focus keywords (comma-separated)", ", ".join(profile.focus_keywords))
    preferred_locations = st.text_input("Preferred locations (comma-separated)", ", ".join(profile.preferred_locations))
    preferred_levels = st.text_input("Preferred levels (comma-separated)", ", ".join(profile.preferred_levels))
    remote_preference = st.selectbox(
        "Remote preference",
        ["any", "remote", "hybrid", "onsite"],
        index=["any", "remote", "hybrid", "onsite"].index(profile.remote_preference),
    )
    salary_min = st.number_input("Minimum salary (USD)", min_value=0, value=int(profile.salary_min or 0), step=5000)
    reputable_only = st.checkbox("Only reputable companies (allowlist)", value=profile.reputable_only)

    st.subheader("Reputable Company Allowlist")
    allowlist = "\n".join(load_reputable_companies())
    allowlist_text = st.text_area("One company per line", allowlist)

    st.subheader("Job Alert Sources")
    alert_sources = st.text_area("RSS or feed URLs (one per line)", "\n".join(profile.alert_sources))

    st.subheader("Alert Email")
    alert_email_to = st.text_input("Send alerts to", profile.alert_email_to or "")
    alert_email_enabled = st.checkbox("Enable email alerts", value=profile.alert_email_enabled)

    if st.button("Save Profile"):
        updated = InterestProfile(
            focus_skills=_split_list(focus_skills),
            focus_domains=_split_list(focus_domains),
            focus_keywords=_split_list(focus_keywords),
            preferred_locations=_split_list(preferred_locations),
            preferred_levels=_split_list(preferred_levels),
            remote_preference=remote_preference,
            salary_min=int(salary_min or 0),
            reputable_only=reputable_only,
            alert_sources=[line.strip() for line in alert_sources.splitlines() if line.strip()],
            alert_email_to=alert_email_to.strip() or None,
            alert_email_enabled=alert_email_enabled,
        )
        save_profile(updated)
        save_reputable_companies([line.strip().lower() for line in allowlist_text.splitlines() if line.strip()])
        st.success("Profile saved")

    st.subheader("Test Alert Email")
    if st.button("Send Test Email"):
        current_profile = load_profile()
        if not resend_key:
            st.error("Resend key missing")
        elif not current_profile.alert_email_to:
            st.error("Add an alert email address first")
        else:
            send_resend_email(
                resend_key,
                current_profile.alert_email_to,
                "Job Finder Test",
                "<p>This is a test alert from Job Finder.</p>",
                from_email=resend_from,
            )
            st.success("Test email sent")
