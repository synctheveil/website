# Veilshift website

Static Hugo site for the Veilshift card game.

The presentation is packaged as the reusable `themes/veilshift` Hugo theme.

## Local development

```sh
mise exec -- hugo server
```

## Production build

```sh
mise exec -- hugo --minify
```

The generated site is written to `public/`.
