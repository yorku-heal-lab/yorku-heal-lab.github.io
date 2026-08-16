# Deployment Guide — HEAL Lab Website

This site is a [Jekyll](https://jekyllrb.com/) static website deployed to **GitHub Pages** using GitHub Actions (the same pattern used by sites like [kolpashnikova.github.io](https://kolpashnikova.github.io)).

## Deployment Options

### Option A: User or Organization Site (recommended)

URL: `https://USERNAME.github.io` or `https://ORG-NAME.github.io`

The repository **must** be named exactly:

- `YOUR-USERNAME.github.io` (personal account), or
- `heal-lab.github.io` (organization account)

The site is served from the **repository root** at `/`.

### Option B: Project Site

URL: `https://USERNAME.github.io/REPO-NAME`

Use any repository name (e.g. `datalab-website`). You must set `baseurl` in `_config.yml`:

```yaml
url: "https://YOUR-USERNAME.github.io"
baseurl: "/REPO-NAME"
```

Rebuild locally with `bundle exec jekyll serve --baseurl "/REPO-NAME"` to preview.

---

## Step-by-Step: Deploy to GitHub Pages

### 1. Create the GitHub repository

1. Go to [github.com/new](https://github.com/new).
2. Create a repository named `heal-lab.github.io` (or `YOUR-USERNAME.github.io`).
3. Do **not** initialize with a README (we already have one).

### 2. Push the site code

From your machine, in the `datalab-website/` directory:

```bash
git init
git add .
git commit -m "Initial HEAL Lab Jekyll site"
git branch -M main
git remote add origin git@github.com:YOUR-ORG-OR-USERNAME/heal-lab.github.io.git
git push -u origin main
```

> **Important:** Push the *contents* of `datalab-website/` to the repo root — not the parent `DATALAB/` folder.

### 3. Enable GitHub Pages

1. Open the repository on GitHub.
2. Go to **Settings → Pages**.
3. Under **Build and deployment → Source**, select **GitHub Actions**.

### 4. Configure site URL

Edit `_config.yml` before pushing (or in a follow-up commit):

```yaml
# For user/org site at root:
url: "https://heal-lab.github.io"
baseurl: ""

# For project site:
# url: "https://YOUR-USERNAME.github.io"
# baseurl: "/datalab-website"
```

Commit and push. The workflow in `.github/workflows/deploy.yml` runs automatically on every push to `main`.

### 5. Verify deployment

1. Go to **Actions** tab in the repository.
2. Confirm the "Deploy Jekyll site to Pages" workflow completed successfully.
3. Visit your site URL (shown in Settings → Pages after first deploy).

First deploy may take 1–2 minutes.

---

## Custom Domain (optional)

1. Create a file named `CNAME` in the repo root:

   ```
   heal-lab.yourdomain.ca
   ```

2. In your DNS provider, add:
   - **CNAME** record pointing to `YOUR-ORG.github.io`, or
   - **A records** to GitHub Pages IPs (see [GitHub docs](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site))

3. In repo **Settings → Pages → Custom domain**, enter your domain and enable HTTPS.

---

## Workflow Details

The deploy workflow (`.github/workflows/deploy.yml`):

1. Checks out the repository
2. Installs Ruby 3.2 and Bundler dependencies
3. Runs `bundle exec jekyll build`
4. Uploads `_site/` as a Pages artifact
5. Deploys to GitHub Pages

No `gh-pages` branch is needed.

---

## Troubleshooting

### Build fails in GitHub Actions

- Open the failed workflow run and read the **Build with Jekyll** step log.
- Common fixes:
  - Ensure `Gemfile.lock` is committed (run `bundle install` locally first).
  - Fix YAML syntax errors in `_data/*.yml` (indentation matters).
  - Avoid unsupported Jekyll plugins (only gems in `Gemfile` are used).

### Site loads but CSS/images are broken

- Check `url` and `baseurl` in `_config.yml` match your deployment type.
- For project sites, `baseurl` must match the repo name exactly (leading slash, no trailing slash).

### Local build works but Actions fails

```bash
JEKYLL_ENV=production bundle exec jekyll build
```

Run locally to reproduce production build errors.

### Ruby / Bundler issues locally

```bash
gem install bundler
bundle install
```

On Ubuntu, if native extensions fail:

```bash
sudo apt-get install ruby-dev build-essential
```

### Pages not updating after push

- Check Actions tab for a green checkmark on the latest run.
- Hard-refresh browser (Ctrl+Shift+R) or wait a few minutes for CDN cache.

---

## Updating Site Content

Most pages are driven by spreadsheets in `scripts/data/`. Edit the spreadsheet, run the matching sync script to regenerate `_data/*.yml`, preview locally, then commit and push.

### One-time setup (Python sync scripts)

```bash
pip install -r scripts/requirements.txt
```

Requires Python 3.9+ with `openpyxl` and `PyYAML`.

### General workflow

1. Edit the spreadsheet in `scripts/data/`.
2. Run the sync script (use `--dry-run` to preview without writing files).
3. Preview the site: `bundle exec jekyll serve --livereload`
4. Commit both the spreadsheet and the updated `_data/*.yml` files, then push to `main`.

```bash
python3 scripts/sync_news_from_xlsx.py --dry-run
python3 scripts/sync_news_from_xlsx.py
```

### Content by section

| Page / section | Spreadsheet | Sync script | Output |
|----------------|-------------|-------------|--------|
| Home (co-directors), Team | `scripts/data/HEAL lab info for website.xlsx` | `scripts/sync_from_xlsx.py` | `_data/lab.yml`, `_data/team.yml` |
| Publications | `scripts/data/publications.xlsx` | `scripts/sync_publications_from_xlsx.py` | `_data/publications.yml` |
| News | `scripts/data/news.xlsx` | `scripts/sync_news_from_xlsx.py` | `_data/news.yml` |
| Resources | `scripts/data/resources.xlsx` | `scripts/sync_resources_from_xlsx.py` | `_data/resources.yml` |
| Research | `scripts/data/research.xlsx` | `scripts/sync_research_from_xlsx.py` | `_data/research.yml` |

---

#### Team and co-directors

**Spreadsheet:** `scripts/data/HEAL lab info for website.xlsx`

**Script:**

```bash
python3 scripts/sync_from_xlsx.py
```

**Columns:**

| Column | Description |
|--------|-------------|
| name to display | Full name shown on the site |
| role in the lab | e.g. Co-Director, PhD student, Postdoctoral Researcher |
| role outside (if any) | Optional secondary role |
| short bio | Biography text (truncated on team page with “Read more”) |
| publication list (at Lab) | Google Scholar or personal website URL |
| York contact info (email) | Email address |
| research interests (keywords) | Comma-separated keywords |
| link to profile image to use | Image filename or path; copied to `assets/images/team/` |

**Notes:**

- Rows with **Co-Director** in “role in the lab” populate the home page and `_data/lab.yml` (not the team page).
- Other members are grouped into postdocs, PhD students, master's students, or collaborators based on role keywords, sorted alphabetically by first name.
- Profile images embedded in the spreadsheet are extracted automatically; otherwise a placeholder is used.

---

#### Publications

**Spreadsheet:** `scripts/data/publications.xlsx`

**Script:**

```bash
python3 scripts/sync_publications_from_xlsx.py
```

**Format:** Each publication uses **three rows**:

1. **Title row** — column A: title, column B: citation count, column C: year
2. **Authors row** — column A: author list
3. **Venue row** — column A: journal/conference details

**Links:** Paper URLs are read from **hyperlinks on the title cell** (column A), not from plain text. The publication title on the site links to that URL and opens in a new tab.

**Deduplication:** The sync script removes duplicate entries by normalized title and by shared paper URL, keeping the most complete record (year, venue, authors, link). The run summary reports how many duplicates were removed.

---

#### News

**Spreadsheet:** `scripts/data/news.xlsx`

**Script:**

```bash
python3 scripts/sync_news_from_xlsx.py
```

**Columns:** `date`, `title`, `summary`, `link` (optional — internal path or full URL)

Dates accept `YYYY-MM-DD` or common formats like `MM/DD/YYYY`. Items are sorted newest first.

---

#### Resources

**Spreadsheet:** `scripts/data/resources.xlsx`

**Script:**

```bash
python3 scripts/sync_resources_from_xlsx.py
```

**Columns:** `section`, `name`, `description`, `url`, `tags` (optional — separate with `;`, `,`, or newlines)

Sections keep spreadsheet order; items within each section are sorted alphabetically by name.

---

#### Research

**Spreadsheet:** `scripts/data/research.xlsx`

**Script:**

```bash
python3 scripts/sync_research_from_xlsx.py
```

**Columns:** `section`, `format`, `title`, `description`, `url` (optional)

| format | Renders as |
|--------|------------|
| `theme` | Heading + paragraph (research themes) |
| `list` | Bullet list with bold title (current projects) |

If `format` is blank, sections containing “project” default to `list`; others default to `theme`. Linked project titles open in a new tab.

---

#### Manual edits (no spreadsheet)

These are edited directly as Markdown or YAML:

| What | File |
|------|------|
| Navigation menu | `_data/navigation.yml` |
| Lab name, tagline, about text, contact, footer | `_data/lab.yml` (contact/footer not overwritten by team sync) |
| Join Us page | `join.md` |
| Page subtitles | Front matter in each page (e.g. `research.md`, `team.md`) |
| Site URL and title | `_config.yml` |
| Images (logos, banners) | `assets/images/` |

---

## Updating the Live Site

1. Update content using the spreadsheets and sync scripts above (or edit Markdown/YAML directly).
2. Preview: `bundle exec jekyll serve --livereload`
3. Commit and push to `main`:

   ```bash
   git add .
   git commit -m "Update publications"
   git push
   ```

4. GitHub Actions redeploys automatically.

---

## Repository Checklist

- [ ] Repo named `*.github.io` (for root URL) or `baseurl` configured (for project site)
- [ ] `_config.yml` `url` and `baseurl` set correctly
- [ ] GitHub Pages source set to **GitHub Actions**
- [ ] First workflow run succeeded
- [ ] Site accessible at expected URL
