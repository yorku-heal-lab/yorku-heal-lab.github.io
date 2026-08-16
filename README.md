# HEAL Lab Website

Jekyll website for the **HEAL Lab** (Health, Evidence, Analytics & Learning) at York University, directed by Dr. Vijay Mago.

## Local Preview

### Option 1: Ruby (native)

On Ubuntu/Debian:

```bash
sudo apt-get update
sudo apt-get install -y ruby-full build-essential zlib1g-dev
cd datalab-website
bundle install
bundle exec jekyll serve --livereload
```

Open [http://127.0.0.1:4000](http://127.0.0.1:4000) in your browser.

### Option 2: Docker (no Ruby install needed)

```bash
cd datalab-website
docker run --rm -it -p 4000:4000 -v "$PWD:/site" -w /site ruby:3.2-bookworm bash -lc \
  "apt-get update -qq && apt-get install -y -qq build-essential && gem install bundler && bundle install && bundle exec jekyll serve --host 0.0.0.0"
```

Open [http://127.0.0.1:4000](http://127.0.0.1:4000) in your browser.

To test as a **project site** (subpath deployment), run:

```bash
bundle exec jekyll serve --baseurl "/repo-name"
```

Then open `http://127.0.0.1:4000/repo-name/`.

### Build only

```bash
bundle exec jekyll build
```

Output is written to `_site/`.

## Updating Content

| What to update | File |
|----------------|------|
| Lab name, PI bio, contact info | `_data/lab.yml` |
| Navigation tabs | `_data/navigation.yml` |
| Team members | `_data/team.yml` + photos in `assets/images/team/` |
| Publications | `_data/publications.yml` |
| News | `_data/news.yml` |
| Research page text | `research.md` |
| Join Us page text | `join.md` |

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for GitHub Pages setup instructions.

## Site Structure

- **Home** — PI profile, bio, research interests, recent news/publications
- **Research** — Research themes and projects
- **Publications** — Full publication list
- **Team** — Current members, collaborators, alumni
- **News** — Lab announcements
- **Join Us** — Open positions and how to apply
