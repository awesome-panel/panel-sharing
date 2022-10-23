## Create Github App

- Go to https://github.com/settings/applications/new and create the application
- Note down the Client ID and Generate an new client secret (KEEP THIS SECRET)

## Configure ENVIRONMENT Variables

- Set the ENVIRONMENT VARIABLES
  - `PANEL_OAUTH_PROVIDER`
  - `PANEL_OAUTH_KEY`
  - `PANEL_OAUTH_SECRET`
  - `PANEL_OAUTH_REDIRECT_URI` (optional)
- Create a Cookie Secret via `panel secret` and set the environment variable
  - `PANEL_COOKIE_SECRET`
- Create an OAuth Secret via `panel oauth-secret` and set the environment variable
  - `PANEL_OAUTH_ENCRYPTION`

## Resources

- https://testdriven.io/blog/oauth-python/
- https://gist.github.com/frankie567/63d499a288e2858869c062b2c652d0fd
- https://docs.github.com/en/developers/apps/building-oauth-apps/creating-an-oauth-app