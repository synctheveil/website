# Sync the Veil website

Static Hugo site for the Sync the Veil card game.

The presentation is packaged as the reusable `themes/sync-the-veil` Hugo theme.

## Local development

```sh
mise exec -- hugo server
```

## Production build

```sh
mise exec -- hugo --minify
```

The generated site is written to `public/`.
