# polskieskille.pl

Static website for [Polskie Skille](https://github.com/b44x/ai-polish-skills), the open-source registry of AI agent skills for Polish services, APIs and public data.

- No build step, no dependencies: plain `index.html`.
- The skill catalogue is loaded live from
  [`registry.min.json`](https://raw.githubusercontent.com/b44x/ai-polish-skills/main/registry/registry.min.json)
  on the `main` branch of `ai-polish-skills`, so new skills appear here automatically after they are merged.
- `llms.txt` points language models to `AGENTS.md` and the registry.

## Files

| Path | Purpose |
|---|---|
| `index.html` | The whole site (hero, demo video, how it works, live catalogue, agent section) |
| `assets/demo.mp4`, `assets/demo-poster.jpg` | Demo video (copied from `ai-polish-skills/docs/demo`) |
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

To refresh the demo video, copy `docs/demo/demo.mp4` from `ai-polish-skills` into `assets/`.

## License

MIT © Michell Hoduń
