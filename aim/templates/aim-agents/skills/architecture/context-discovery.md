# Gathering Context

No architecture should be proposed in a vacuum. Pull the relevant facts out of the user before sketching anything.

## Ask These First, in Priority Order

1. **Scale**
   - Roughly how many users are expected? (tens, a thousand, a hundred thousand, millions and up)
   - How much data will the system hold? (megabytes, gigabytes, terabytes)
   - What throughput is realistic? (requests or transactions per second or minute)

2. **Team**
   - One developer, or a group?
   - If a group, how large and how experienced?
   - Are they in one place or spread across locations?

3. **Timeline**
   - Is this a quick prototype/MVP or a product meant to last?
   - How much pressure is there to ship soon?

4. **Domain**
   - Mostly create-read-update-delete, or genuinely complex business rules?
   - Any real-time behavior required?
   - Are there compliance or regulatory obligations?

5. **Constraints**
   - What's the budget?
   - Any legacy systems that have to be integrated?
   - Existing preferences or mandates around the tech stack?

## Placing the Project on a Spectrum

Once the answers are in, most projects land near one of three profiles. Use this to calibrate how much structure is appropriate.

| Dimension | MVP | SaaS | Enterprise |
|-----------|-----|------|------------|
| Expected scale | under ~1K users | ~1K–100K users | 100K+ users |
| Team | one developer | roughly 2–10 | 10 or more |
| Horizon | weeks | months | years |
| Architecture style | keep it simple | modular | distributed |
| Pattern usage | bare minimum | applied selectively | broad and deliberate |
| Representative stack | a full-stack framework with API routes | a modular backend framework | a set of microservices |
