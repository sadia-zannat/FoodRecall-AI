# Minimum credible operational evidence for FoodRecall AI

**No real company data was supplied for this release.** The included inventory and EPCIS files are artificial training examples. Publicly available FDA enforcement reports are not an authoritative map of stock held by a business.

| Evidence source | Minimum read-only fields | Purpose |
| --- | --- | --- |
| Product master (authorized company) | issuer, GTIN, internal SKU, brand, product description, effective dates | Resolve exact identity; no name-only matching |
| Regulator/manufacturer recall | agency, recall ID, effective/published dates, affected GTIN and lot ranges, precise primary source/version | Establish actual recall scope |
| Warehouse inventory | warehouse ID, GTIN, supplier or lot ID, available/held quantity, captured_at | Candidate exposure at specific time |
| Shipment/receiving | shipment ID, sender, receiver, event timestamp, GTIN, lot ID, quantity, document ID | Chain of custody / receiving proof |
| Supplier documents | invoice/COA/manifest ID, issuer, dates, lot references, signed/approved state | Verify or disprove ambiguous attribution |
| Operational read-back (approved integration only) | action ID, actor, affected lot IDs, resulting state, timestamps | Verify a human-approved containment action |

**Conservative policy:** verify issuer, GTIN and lot identifiers (preserving leading zeroes), source version and timestamps; separate candidate from verified physical match. Missing or conflicting evidence must remain `REVIEW`, not `CONFIRMED`. Source text is untrusted, including emails, PDFs and tool outputs. Never use free-text product-name similarity alone to authorize a hold.

Recommended first live dataset: a small legally authorized inventory export with a few independently verified real recall-to-GTIN-to-lot mappings, and a separate set of known false matches. Store redacted/non-sensitive samples only if redistribution is licensed; keep original data within the customer's private tenant.

No sample 'real warehouse' data is fabricated or bundled here.
