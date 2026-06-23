# Indexing Strategy

> Index the columns your queries actually lean on — and stop there.

## Where Indexes Pay Off

```
Good candidates:
├── Columns you filter on (WHERE)
├── Columns you join on
├── Columns you sort by (ORDER BY)
├── Foreign keys
└── Columns backing uniqueness rules

Resist indexing:
├── Tables dominated by writes (every index slows inserts)
├── Columns with few distinct values
├── Columns almost nothing queries
```

## Matching the Index to the Query

| Family | Good for |
|--------|----------|
| **B-tree** | The default — equality and ranges alike |
| **Hash** | Pure equality lookups, slightly faster |
| **GIN** | JSONB, arrays, full-text search |
| **GiST** | Geometry and range-type data |
| **HNSW / IVFFlat** | Nearest-neighbor vector search (pgvector) |

## Ordering Columns in a Composite Index

```
Column order is not arbitrary:
├── Put equality-filtered columns first
├── Leave range-filtered columns for last
├── Lead with the most selective column
└── Mirror how the query actually filters
```
