# REST

> Design around resources. Name things as nouns; let HTTP verbs carry the action.

## Naming resources

```
Conventions that age well:
├── Nouns for resources, never action words
├── Plural collections — /orders, not /order
├── Lowercase with hyphens — /shipping-labels
├── Nest to show ownership — /orders/42/items
└── Stay shallow — three levels is plenty
```

## Choosing the method

| Verb | What it means | Idempotent? | Sends a body? |
|------|---------------|-------------|---------------|
| **GET** | Fetch one or many | Yes | No |
| **POST** | Create something new | No | Yes |
| **PUT** | Replace the whole resource | Yes | Yes |
| **PATCH** | Change part of it | No | Yes |
| **DELETE** | Remove it | Yes | No |

## Choosing the status code

| What happened | Code | Reasoning |
|---------------|------|-----------|
| Read succeeded | 200 | The everyday success |
| Resource created | 201 | Something new now exists |
| Done, nothing to send | 204 | Success with an empty body |
| Request was malformed | 400 | Client sent something broken |
| Caller not authenticated | 401 | Credentials missing or invalid |
| Authenticated but not allowed | 403 | Identity known, access denied |
| Nothing matches | 404 | The resource isn't there |
| Clashes with current state | 409 | e.g. a duplicate |
| Well-formed but invalid data | 422 | Syntax fine, semantics off |
| Over the quota | 429 | Caller is sending too fast |
| Something broke on our side | 500 | Server fault, not the client's |
