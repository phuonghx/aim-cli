# Authentication Choices

> Match the mechanism to how callers actually use the API.

## Picking a scheme

| Scheme | Where it shines |
|--------|-----------------|
| **JWT** | Stateless services, horizontally scaled fleets |
| **Server sessions** | Classic server-rendered web apps; simplest to reason about |
| **OAuth 2.0** | Letting third parties act on a user's behalf |
| **API keys** | Machine-to-machine calls, published developer APIs |
| **Passkeys** | Phishing-resistant, password-free sign-in |

## Getting JWTs right

A handful of habits keep token auth safe:

```
Non-negotiables:
├── Validate the signature on every request
├── Reject anything past its expiry
├── Keep the payload lean — claims only, no secrets
├── Pair short-lived access tokens with refresh tokens
└── Treat the token body as public; never put private data in it
```
