# Public data

One week of production sessions (2026-09-21 to 2026-09-28), 400 sessions across about 170 businesses. Some businesses have several sessions.

## `sessions/<session_id>.json`

See `INTERFACE.md` for the schema. Tools that appear in this set: `deploy_site`, `list_orders`, `send_email`, `launch_ad`, `ad_status`, `buy_domain`, `upload_file`, `post_social`, `request_payout`. Every tool result follows the receipt contract `{ok, id?, status?, error?, ...}`.

`state` entity types you will see: `deploy`, `order`, `email`, `ad`, `domain`, `file`, `post`, `payout`. Status vocabularies are tool-specific (`delivered`, `registered`, `paid`, `published`, `active`, `paused`, `refunded`, ...). Orders carry `amount`, `customer`, `customer_name`, `product`. Ads carry a `spend` ledger that moves over time. Emails sent to several recipients are one entity per recipient, tied together by a `batch` field.

Things to know about receipts, all visible in this set:

- `id` is optional. Some integrations return attributes instead (`to`, `url`, `domain`, `name`, `amount`) and the matching state entity carries the same attributes.
- Calls get retried. A timed-out or errored first attempt can be followed by a second call with a different id, and the first attempt sometimes went through anyway.
- `list_orders` takes a `since` window (`24h`, `48h`, `7d`, `all`) and the agent talks about "today", "since yesterday", "this week", "so far". Refunded orders are not paid orders.
- The `state` array is in write order, not event order. Sort by `ts`.

## `labels.jsonl`

One row per labeled claim: `{"session_id", "turn_index", "span": [start, end], "text", "category", "verdict", "attribution"}`. `span` indexes into the agent turn's `content`; `text` is exactly `content[start:end]`. About 1.9k claims.

## `support/`

- `tickets.jsonl`: `{ticket_id, business_id, created_at, session_id|null, subject, body, category, status, mentioned_turn_index|null}`
- `refunds.jsonl`: `{refund_id, business_id, ts, amount, reason, session_id|null}`
- `churn.jsonl`: `{business_id, churned_at, reason, last_session_id, plan}`

`session_id` links a support event to the session the owner was complaining about, when support could identify one. Use it however you like; it is not part of the scored interface.
