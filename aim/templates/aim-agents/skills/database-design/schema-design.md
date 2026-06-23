# Modeling Tables

> Normalization, keys, time columns, and how rows relate.

## Normalize or Denormalize?

```
Split data into its own table when:
├── The same values recur across many rows
├── A single edit would otherwise touch many places
├── The entities are genuinely distinct
└── Your query shapes reward the separation

Fold data together (duplicate / embed) when:
├── Read speed is the priority
├── The values almost never change
├── It is always loaded as one unit
└── It keeps the common query simple
```

## Choosing the Primary Key

| Key style | Reach for it when |
|-----------|-------------------|
| **UUID** | Spread across nodes, or IDs shouldn't be guessable |
| **ULID** | You want UUID-style IDs that also sort by creation time |
| **Auto-increment integer** | One database, straightforward app |
| **Natural key** | Only when a real-world identifier truly fits |

## Time Columns

```
Most tables want:
├── created_at → row's birth time
├── updated_at → last touch
└── deleted_at → present only if you do soft deletes

Prefer TIMESTAMPTZ over a naive TIMESTAMP so zones stay correct.
```

## Relationship Shapes

| Shape | Use for | How it's wired |
|-------|---------|----------------|
| **One-to-one** | Optional extension records | Foreign key on a side table |
| **One-to-many** | A parent owning many children | Foreign key sits on the child |
| **Many-to-many** | Each side relates to many | A join table between them |

## Behavior on Parent Delete

```
├── CASCADE     → children vanish with the parent
├── SET NULL    → children stay but lose the link
├── RESTRICT    → deletion is blocked while children remain
└── SET DEFAULT → children fall back to a default reference
```
