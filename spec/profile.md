# Quilt RO-Crate profile

Version 0.2.0 — 2026-09-25 — **draft**

An [RO-Crate](https://www.researchobject.org/ro-crate/) profile for crates that are
ingested into [Quilt](https://docs.quiltdata.com/) packages.

| | |
|---|---|
| Profile URI | <https://w3id.org/quilt/ro-crate> |
| This version | `https://w3id.org/quilt/ro-crate/0.2` |
| Previous version | [`https://w3id.org/quilt/ro-crate/0.1`](https://w3id.org/quilt/ro-crate/0.1) |
| Term namespace | `https://w3id.org/quilt/ro-crate#` |
| `isProfileOf` | [RO-Crate 1.2](https://w3id.org/ro/crate/1.2) minimum; [1.3](https://w3id.org/ro/crate/1.3) permitted |
| Recommended companion | [Process Run Crate 0.6](https://w3id.org/ro/wfrun/process/0.6) |
| Source | <https://github.com/quiltdata/quilt-ro-crate-profile> |

## Purpose

Instruments and acquisition software increasingly emit an `ro-crate-metadata.json`
alongside their output. That graph already names the files produced, who ran the
experiment, on which instrument, and when. A profile lets a packaging system read it
directly instead of requiring a separate, system-specific manifest.

This profile **requires** only what a packaging system needs to build the package a crate
describes:

1. the exact set of files to package
2. the target package name, when the producer chooses one

It **recommends** how to express three more things, so that a consumer can index them for
search without site-specific configuration:

3. the people and organizations responsible
4. the instrument that produced the data, and the acquisition event
5. the electronic lab notebook entry the work belongs to

Everything else is up to the producer, and is passed through untouched.

## Conformance

The key words MUST, MUST NOT, REQUIRED, SHOULD, SHOULD NOT, RECOMMENDED, MAY and OPTIONAL
are to be interpreted as described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

Requirements are split between **producers** (whatever writes the crate) and **consumers**
(whatever reads it to build a package). Both sets are normative.

A crate that meets the [producer requirements](#producer-requirements) conforms. The
[producer recommendations](#producer-recommendations) are SHOULDs: a crate that departs from
one still conforms and is still packaged, and the consumer derives less search metadata
from it.

## Design principles

These explain why the requirements look the way they do. They are not themselves normative.

**Require only what ingestion needs.** A requirement exists only where getting it wrong
would make the package wrong: files missing, or a package under a name the producer did not
intend. How a crate models people, instruments, actions and notebook entries is the
producer's decision. The recommendations are the patterns a consumer reads for search; a
crate that models things differently loses those search fields, not its package.

**schema.org first.** [RO-Crate's guidance](https://www.researchobject.org/ro-crate/specification/1.3/appendix/jsonld.html#extending-ro-crate)
is to use existing schema.org terms, accepting a liberal reading, before inventing
anything. Applied strictly, this profile needs three new terms.

**No new JSON-LD keys.** All three terms are `DefinedTerm`s referenced by `@id`, as values
of `propertyID` and `additionalType`. Neither is a key position, so **a conforming crate
needs no `@context` extension** and parses correctly under stock RO-Crate tooling. An
unmapped term in a key or `@type` position is silently dropped by any JSON-LD processor;
avoiding those positions removes a whole class of quiet data loss.

**The crate does not model the consumer's search index.** It is tempting to bend the crate
so its keys match the facets a catalog wants to display. That inverts the dependency: the
crate becomes unchangeable because a search schema depends on its shape. Instead, crates
stay idiomatic and consumers derive whatever projection they need at ingest.

**Vendor-neutral where the vendor is incidental.** An `@type` naming a specific notebook
product cannot generalize to a second product. A typed entity with a `provider` can.

## Producer requirements

### Manifest

- The root data entity MUST declare a non-empty `hasPart` listing every file or directory
  to be packaged. This list is the manifest.
- A relative `@id` in `hasPart` resolves against the folder holding
  `ro-crate-metadata.json` and MUST stay inside it: no `.` or `..` segments, no empty
  segments, no leading `/`. Being a URI reference, it is percent-decoded, so a `?` or `#`
  that belongs to the key MUST be percent-encoded. An absolute `s3://` `@id` may name an object anywhere; its
  basename becomes the package logical key.
- A directory MUST be typed `Dataset` or have an `@id` ending in `/`. It expands to every
  object beneath that prefix.
- An `http://` or `https://` member is a reference to something on the web rather than an
  object that can be packaged, and is left out of the package. (nf-prov, for instance, lists
  the license URL there.)
- Members MUST map to distinct logical keys. Two absolute `s3://` members with the same
  basename collide, as do two directories that expand to one key holding different
  objects. A file listed explicitly that a directory member also covers is fine when both
  name the same object; the file keeps its entry metadata.
- Two entities MUST NOT share an `@id` with different content. A verbatim repeat, which some
  emitters produce, is treated as one entity.

### Package naming

Naming is optional; without it the consumer uses its own default. To choose the name, the
root data entity carries one of the following under `identifier`.

Fully qualified name:

```json
{
  "@id": "#quilt-package-name",
  "@type": "PropertyValue",
  "propertyID": "https://w3id.org/quilt/ro-crate#packageName",
  "value": "my-namespace/2026-09-08-assay-01"
}
```

Namespace only, with the name derived from the root entity's `name`:

```json
{
  "@id": "#quilt-namespace",
  "@type": "PropertyValue",
  "propertyID": "https://w3id.org/quilt/ro-crate#packageNamespace",
  "value": "my-namespace"
}
```

This mirrors how the base specification expresses a DOI: a `PropertyValue` under
`identifier`, distinguished by `propertyID`. It needs no new JSON-LD key.

- A `packageName` value MUST already be a valid Quilt package name: two parts of letters,
  digits, `_` or `-`, separated by one `/`. A `packageNamespace` value MUST be a valid first
  part. Consumers reject rather than normalize, so that a malformed name surfaces at the
  producer.
- A crate MUST NOT give two different values for either term.
- The root's `name` is a title written for people, so when it is joined to a
  `packageNamespace` the consumer adapts it to the package-name grammar as the
  [consumer requirements](#consumer-requirements) define. A producer that needs an exact
  name gives `packageName` instead.

## Producer recommendations

Each recommendation below says what a consumer reads from it. A crate that departs from one
is still packaged.

### Metadata document

- The RO-Crate Metadata Descriptor SHOULD set `conformsTo` to
  `https://w3id.org/ro/crate/1.2` or `https://w3id.org/ro/crate/1.3`. Consumers determine
  the RO-Crate version from this property, [not from `@context`](https://www.researchobject.org/ro-crate/specification/1.3/appendix/jsonld.html).
- `@context` SHOULD be the matching versioned RO-Crate context, with no additional entry.
- The document SHOULD be flattened and compacted, as RO-Crate asks: every entity a direct
  child of `@graph`, every reference an object whose only key is `@id`.
- Properties SHOULD be omitted rather than given a `null` value.
- The file SHOULD be UTF-8 **without** a byte-order mark. A BOM makes strict JSON parsers
  fail outright, and some common tooling adds one by default — notably Windows PowerShell's
  `Out-File` and `ConvertTo-Json` before `-Encoding utf8NoBOM` was available.

### Root data entity

The [base specification](https://www.researchobject.org/ro-crate/specification/1.3/root-data-entity.html)
requires `name`, `description`, `datePublished` and `license` on the root data entity. This
profile adds nothing to those requirements and does not enforce them. In addition, the root
data entity:

- SHOULD declare `conformsTo` including `{"@id": "https://w3id.org/quilt/ro-crate"}`, with a
  corresponding contextual entity typed `["CreativeWork", "Profile"]`. This tells readers and
  tools which conventions the crate follows; it does not change how a consumer processes it.
- SHOULD declare `creator`, `producer`, `mentions` and `subjectOf`, which are what a consumer
  reads for search metadata, as described below. `keywords` is also RECOMMENDED.

### File entities

Each `File` SHOULD carry `name`, `encodingFormat`, `contentSize`, `dateCreated`,
`dateModified` and `sha256`. A consumer attaches every property except `@id`, `@type` and
`name` to the package entry, whose logical key already names the file.

`dateCreated` and `dateModified` SHOULD be the times the instrument produced the data, not
the times the files were transferred or copied. Object stores overwrite filesystem
timestamps on upload, so these properties are frequently the only surviving record of when
an experiment actually ran. The two are often equal; that is expected and correct.

### People and organizations

A consumer reads the `name` of each root `creator` and `producer`, following
`parentOrganization` from each producer.

- A `Person` `@id` SHOULD be an absolute URI — an [ORCID](https://orcid.org/) where one
  exists, otherwise a URI the institution controls. A bare fragment such as `#jdoe` is not
  resolvable and not stable across crates.
- `name` SHOULD be the human-readable full name, with a login, account or notebook handle
  given as `alternateName`. Carrying both means nobody has to infer whether a handle in one
  system matches an account name in another.
- A parent and child organization SHOULD both be `Organization`, linked from child to parent
  with `parentOrganization`.

### Instruments and acquisition

A consumer finds instruments through the root's `mentions`: it reads the `name` and
`identifier` of each listed action's `instrument`.

To make an acquisition findable, record it following
[Process Run Crate](https://www.researchobject.org/workflow-run-crate/profiles/process_run_crate/):
a `CreateAction` carrying `instrument`, `agent`, `result` and `endTime`, listed under the
root entity's `mentions`. Without `mentions` the action is unreachable from the root and a
generic consumer cannot find it.

A physical instrument SHOULD be an `IndividualProduct` — schema.org's type for a single
identifiable unit — with an absolute URI as `@id`, a human-readable `name`, and an
`identifier` unique to the instrument. It SHOULD also carry `manufacturer`, `model`, and
`additionalType` referencing an ontology IRI for the instrument class; see
[ontology-iri-lookup.md](../docs/ontology-iri-lookup.md) for how to find one. The owning
organization SHOULD link to the instrument with schema.org's existing `owns` property.

Any other actions in the crate, such as software processing steps, are up to the producer.
Process Run Crate describes how to record them, and declaring conformance to it alongside
this profile is RECOMMENDED.

### Electronic lab notebook entry

A consumer reads the `name` of each root `subjectOf` entity whose `additionalType` is
`ELNEntry`.

```json
{
  "@id": "https://eln.example.org/entries/etr_AbC123",
  "@type": "CreativeWork",
  "additionalType": { "@id": "https://w3id.org/quilt/ro-crate#ELNEntry" },
  "name": "ASSAY-1234",
  "identifier": "etr_AbC123",
  "url": "https://eln.example.org/entries/etr_AbC123",
  "provider": { "@id": "#eln-vendor" }
}
```

The `@id` SHOULD be the resolvable entry URL, which makes the identifier globally unique
without reserving any identifier space per vendor. `provider` SHOULD reference an
`Organization` or `SoftwareApplication` naming the notebook system, which is what lets one
consumer tell several notebook systems apart.

### Licensing

`license` is required on the root entity by the base specification. A consumer of this
profile does not read it; this section is guidance for meeting that requirement when no
public license applies — internal or proprietary data being the common case. Define a local
`CreativeWork` and reference it identically from every crate:

```json
"license": { "@id": "https://example.org/legal/internal-research-use/1.0" },
"copyrightHolder": { "@id": "https://example.org/org/example-institute" },
"copyrightYear": "2026",
"conditionsOfAccess": "Internal use only. Access governed by the owning group.",
"isAccessibleForFree": false
```

```json
{
  "@id": "https://example.org/legal/internal-research-use/1.0",
  "@type": "CreativeWork",
  "name": "Example Institute internal research use v1.0",
  "description": "Proprietary and confidential. All rights reserved. Internal research use only; no redistribution or publication without written authorization.",
  "sameAs": "http://rightsstatements.org/vocab/InC/1.0/"
}
```

Points worth noting:

- **Version the license URI.** Revising the terms then does not silently re-license crates
  already published.
- **The URI need not be publicly resolvable.** The base specification says it SHOULD be the
  license's URL; an intranet URL satisfies that. Carry the terms inline in `description` so
  the crate remains self-describing when the URL is unreachable.
- **`copyrightHolder` is the legal entity**, distinct from `creator` (the individual) and
  `producer` (the group). Three different claims.
- **`license` and access control are different things.** `license` states what may be done
  with the data; `conditionsOfAccess` and `isAccessibleForFree` state who may obtain it.
  Both are in the RO-Crate context. Note that while the base specification's section is
  titled "Licensing, Access control and copyright", its body addresses `license` and
  `copyrightHolder` only, so `conditionsOfAccess` here is ordinary schema.org rather than a
  specific base-specification recommendation.
- **`sameAs` to a [RightsStatements.org](https://rightsstatements.org/) URI is OPTIONAL.**
  `InC` ("In Copyright") is a widely deployed controlled value for "copyrighted, not openly
  licensed". That vocabulary was designed for cultural heritage collections, so it is a
  serviceable rather than exact fit.

Three things to avoid:

- **Do not apply a Creative Commons license to data that is not openly licensed.** CC
  grants are public and irrevocable. It is a one-way door, not a placeholder.
- **Do not use an SPDX identifier.** SPDX has no listed identifier for proprietary terms;
  `LicenseRef-` strings are a software-bill-of-materials convention.
- **Do not omit `license`.** Omitting it makes the crate invalid rather than unlicensed.

An alternative, used by the
[Language Data Commons profile](https://purl.archive.org/textcommons/profile), is to ship
the terms as a file inside the crate and point `license` at it. That maximizes
self-containment and suits crates that travel between institutions, at the cost of
duplicating the file into every crate.

### Additional metadata

Anything not covered above SHOULD be expressed with `variableMeasured` referencing a
`PropertyValue` carrying `propertyID`, `value` and, where applicable, `unitText`. This may
appear on the root entity or on individual files. It is the same pattern the
[ELN file format](https://github.com/TheELNConsortium/TheELNFileFormat) uses, including `.`
as a nesting separator within `propertyID`.

Producers SHOULD NOT introduce bare JSON keys for this purpose, because JSON-LD processing
drops an unmapped key, and with it the value, in most RO-Crate tooling.

The `propertyID` IRIs here belong to the producer, under a namespace the producer controls.
This profile deliberately does not enumerate them: that is the extension point which keeps
domain-specific metadata independent of this profile's versioning.

## Terms defined by this profile

Three, all `DefinedTerm`, all referenced by `@id` only. They are defined in the
[Profile Crate](../0.2/ro-crate-metadata.json) and, per the
[profiles specification](https://www.researchobject.org/ro-crate/specification/1.2/profiles.html),
need not be repeated in each conforming crate.

| Term | Used as | Meaning |
|---|---|---|
| [`packageName`](https://w3id.org/quilt/ro-crate#packageName) | `propertyID` | Fully qualified package name, `namespace/name` |
| [`packageNamespace`](https://w3id.org/quilt/ro-crate#packageNamespace) | `propertyID` | Namespace only; name derived from the root entity's `name` |
| [`ELNEntry`](https://w3id.org/quilt/ro-crate#ELNEntry) | `additionalType` | Marks a `CreativeWork` as an electronic lab notebook entry |

Term IRIs are intentionally unversioned while the profile URI is versioned, so that terms
remain stable across profile revisions.

## Consumer requirements

A conforming consumer is one that builds a package from a crate.

**Manifest.** The consumer MUST package exactly the entities listed in the root entity's
`hasPart`, expanding each directory member — one typed `Dataset` or with an `@id` ending in
`/` — to the objects beneath it, and leaving out `http://` and `https://` members. It MUST NOT substitute a directory listing when a crate
is present.

**Package naming.** Resolution order MUST be: an explicit `packageName`; otherwise
`packageNamespace` joined to the root entity's `name`; otherwise the consumer's own
default. An invalid explicit name or namespace MUST be rejected rather than corrected.

When joining a `packageNamespace` to the root's `name`, the consumer MUST replace each
character other than a letter, digit, `_` or `-` with `-`, so `Assay A/B` becomes
`Assay-A-B`. If the root has no `name`, or nothing but `-` remains, the consumer MUST use
the name part of its own default.

**Entry metadata.** For each `File`, the consumer SHOULD attach the entity's remaining
properties — everything except `@id`, `@type` and `name` — as metadata on the corresponding
package entry, so that instrument timestamps and checksums survive into the package.

**Package metadata.** The consumer SHOULD derive a flat projection for search, keyed by the
role an entity plays rather than by its `@type`, and reading each role as the
[recommendations](#producer-recommendations) describe:

```json
{
  "package_name": "my-namespace/2026-09-08-assay-01",
  "creator":       ["Jane Doe"],
  "producer":      ["Assay Development", "Laboratory Operations"],
  "instrument":    ["Flow Cytometer 1"],
  "instrument_id": ["INST-000123"],
  "eln_entry":     ["ASSAY-1234"]
}
```

Keying by role rather than type is what makes this stable. Two entities of the same type —
a parent and child organization, say — are distinguished by the property that links them to
the root, not by inventing compound keys from their identifiers. Values stay
human-readable, because a scientist searches for a group or instrument name, not for a key.
A role the crate does not express is omitted. The consumer SHOULD read an entity written
inline the same as one referenced by `@id`.

**Provenance.** The consumer MUST include `ro-crate-metadata.json` in the package, so the
package records, verbatim, the graph it was built from.

**Rejection.** The consumer MUST reject a crate it cannot package as written — a `hasPart`
member it cannot resolve, two members that map to one logical key, an invalid or
conflicting explicit name, two different entities with one `@id` — rather than package
part of it. It MUST NOT reject a crate for departing
from a recommendation, and declaring conformance to this profile does not change how a
crate is processed. It SHOULD decode a UTF-8 byte-order mark rather than fail on one.

## Validation

[`validate.py`](../validate.py) in this repository checks the Profile Crate and its example:
JSON-LD expansion against the published RO-Crate context with no term dropped, the Profile
Crate's structural requirements, resource descriptors and their roles, term definitions
agreeing with the term set in both directions, and the example declaring conformance back to
the profile.

It does not check arbitrary crates against the requirements above; no SHACL shape exists
yet. [`roc-validator`](https://github.com/crs4/rocrate-validator) covers the base
specification layer.

## References

- [RO-Crate 1.3 specification](https://www.researchobject.org/ro-crate/specification/1.3/)
- [RO-Crate profiles](https://www.researchobject.org/ro-crate/specification/1.2/profiles.html)
  and the [profiles registry](https://profiles.ro-crate.org/)
- [Extending RO-Crate](https://www.researchobject.org/ro-crate/specification/1.3/appendix/jsonld.html#extending-ro-crate)
- [Process Run Crate](https://www.researchobject.org/workflow-run-crate/profiles/process_run_crate/)
- [ELN file format specification](https://github.com/TheELNConsortium/TheELNFileFormat)
- [schema.org](https://schema.org/)
- [Quilt documentation](https://docs.quiltdata.com/) and
  [quiltdata/quilt](https://github.com/quiltdata/quilt)

## License

This specification is licensed under the [Apache License 2.0](../LICENSE).
