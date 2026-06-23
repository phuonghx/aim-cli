# Building Features

How to size up a new feature request and ship it safely into an existing project.

## Sizing Up a Request

```
Request: "add a payment system"

Breakdown:
├── What has to change:
│   ├── Database: orders and payments tables
│   ├── Backend: /api/checkout, /api/webhooks/stripe
│   ├── Frontend: CheckoutForm, PaymentSuccess
│   └── Config: Stripe API keys
│
├── What it leans on:
│   ├── the stripe package
│   └── the existing user-authentication flow
│
└── Footprint: DB change + 2 API routes + 2 components + config
```

## The Loop for Each Enhancement

```
1. Survey what the project already has
2. Draft the set of changes
3. Walk the user through the plan
4. Wait for the go-ahead
5. Make the changes
6. Test them
7. Show the preview
```

## When Things Break

| What went wrong | How to handle it |
|-----------------|------------------|
| TypeScript complaint | Correct the type or add the missing import |
| Package not installed | Run npm install |
| Port already taken | Offer a different port |
| Database failure | Recheck the migration and verify the connection |

## Backing Out Cleanly

```
1. Catch the error
2. Attempt a fix on its own
3. If that fails, tell the user
4. Offer another route
5. Roll back when needed
```
