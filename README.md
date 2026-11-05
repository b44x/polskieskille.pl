# polskieskille.pl

Static website for [Polskie Skille](https://github.com/b44x/ai-polish-skills), the open-source registry of AI agent skills for Polish services, APIs and public data.

- GitHub Pages serves committed HTML and assets; no server or JavaScript framework is required.
- A Python standard-library script generates crawlable skill pages and the sitemap before publication.
- The skill catalogue is loaded live from
  [`registry.min.json`](https://raw.githubusercontent.com/b44x/ai-polish-skills/main/registry/registry.min.json)
  on the `main` branch of `ai-polish-skills`, so new skills appear here automatically after they are merged.
- A bundled catalogue renders immediately and remains available when the remote registry is unreachable. The page labels which source is currently displayed.
- `llms.txt` points language models to `AGENTS.md` and the registry.

## Files

| Path | Purpose |
|---|---|
| `index.html` | The whole site (hero, demo video, how it works, live catalogue, agent section) |
| `assets/demo.mp4`, `assets/demo-poster.jpg` | Demo video (copied from `ai-polish-skills/docs/demo`) |
| `assets/registry.min.json` | Bundled fallback catalogue |
| `scripts/sync_catalog.py` | Synchronises the catalogue, demo and poster from the adjacent checkout |
| `content/skills.json`, `scripts/build_seo.py` | Polish page content and static page generator |
| `skille/<name>/index.html` | Skill pages with installation, sources, examples and limitations |
| `scripts/validate_site.py` | Checks metadata, sitemap, structured JSON and internal links |
| `assets/og-image.jpg` | Social preview image |
| `llms.txt`, `robots.txt`, `sitemap.xml`, `404.html` | Discovery and housekeeping |
| `CNAME` | Custom domain for GitHub Pages |

## Local preview

```bash
python3 -m http.server 8000   # then open http://localhost:8000
```

## Deploy (GitHub Pages)

1. Repository → **Settings → Pages** → Source: **Deploy from a branch**, branch `main`, folder `/ (root)`.
2. Custom domain: `polskieskille.pl` (already set by the `CNAME` file), then tick **Enforce HTTPS** once the certificate is issued.
3. DNS at your registrar (remove any parking records first):

   | Type | Name | Value |
   |---|---|---|
   | A | `@` | `185.199.108.153` |
   | A | `@` | `185.199.109.153` |
   | A | `@` | `185.199.110.153` |
   | A | `@` | `185.199.111.153` |
   | AAAA | `@` | `2606:50c0:8000::153` |
   | AAAA | `@` | `2606:50c0:8001::153` |
   | AAAA | `@` | `2606:50c0:8002::153` |
   | AAAA | `@` | `2606:50c0:8003::153` |
   | CNAME | `www` | `b44x.github.io.` |

4. Optional: verify the domain in your GitHub account settings (**Pages → Verified domains**) to prevent domain takeover.

Before publishing a site update with new skills, merge the corresponding skill changes into the source repository's `main` branch so installation links resolve.

Refresh the bundled catalogue, demo and poster from the adjacent checkout (requires ffmpeg for the poster):

```bash
python3 scripts/sync_catalog.py
python3 scripts/sync_catalog.py --catalog-only  # no ffmpeg required
```

Use `--source /path/to/ai-polish-skills` for another checkout. The displayed demo duration is read from the video metadata.

The homepage catalogue is present in the HTML before JavaScript runs. Dedicated skill pages have unique Polish titles and descriptions, canonical URLs, social previews, breadcrumbs and source-code structured data. Search and copy controls enhance this static content in the browser.

After editing Polish content, regenerate and validate the site:

```bash
python3 scripts/build_seo.py
python3 scripts/build_seo.py --check
python3 scripts/validate_site.py
```

The pull-request workflow checks generated pages and internal links. The sitemap is at `https://polskieskille.pl/sitemap.xml`; it can be submitted in Google Search Console after publication. These checks verify the site's implementation, not search rankings or indexing status.

## License

MIT © Michell Hoduń
