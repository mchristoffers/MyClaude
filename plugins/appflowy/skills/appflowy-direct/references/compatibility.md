# Compatibility and authentication

Pinned for Moritz's deployment on 2026-07-30:

- AppFlowy Cloud image `0.17.0`, digest
  `sha256:5a0180744f8ffa49f38e7d3a78797b125ee02059820f2d230b69652daee74667`.
- AppFlowy Web `0.16.1`, source revision
  `031a775a591d09753e28fcb5b7f47f52f3077b6a`.
- GoTrue `0.17.0`.

The public AppFlowy-Cloud repository has no matching `0.17.0` source tag.
Endpoint coverage here is therefore based on the deployed image, GET-only live
probes, the exact Web revision above, and the nearest public Cloud route
snapshot. Recheck routes after upgrades.

Password login is `POST /gotrue/token?grant_type=password`; refresh is the same
path with `grant_type=refresh_token`. `/api` requests use the access token as a
Bearer token. Successful API JSON normally has `{code: 0, data, message}`.

Required environment: `APPFLOWY_BASE_URL`, `APPFLOWY_EMAIL`, and
`APPFLOWY_PASSWORD`. Optional: `APPFLOWY_TOKEN_CACHE` and the non-secret
`APPFLOWY_DEVICE_ID`. The token cache defaults below the XDG runtime/cache
directory with mode `0600`.

The local AI service is intentionally disabled. Treat AI/chat and AI-backed
summary-search routes as unavailable.
