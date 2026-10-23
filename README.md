# Quilt RO-Crate profile

An [RO-Crate](https://www.researchobject.org/ro-crate/) profile for crates that are
ingested into [Quilt](https://docs.quiltdata.com/) packages.

**Status: draft, version 0.3.0.** The 0.3 release artifacts are in [`0.3/`](0.3/).
The versioned URI <https://w3id.org/quilt/ro-crate/0.3> is published and resolving through
GitHub Pages. The unversioned
<https://w3id.org/quilt/ro-crate> currently points to 0.2, pinned by the w3id redirect rules.

Instruments and acquisition software increasingly write an `ro-crate-metadata.json`
alongside their output. That graph already records which files were produced, by whom, on
which instrument, and when. This profile pins down how five things are expressed so that a
packaging system can read the crate directly instead of requiring a separate manifest:

1. the target package name
2. the exact set of files to package
3. the people and organizations responsible
4. the instrument and the acquisition event
5. the electronic lab notebook entry the work belongs to

**Read the specification: [`spec/profile.md`](spec/profile.md).**

## Changes in 0.3

- **ELN linking metadata ([#3](https://github.com/quiltdata/quilt-ro-crate-profile/issues/3)).**
  Consumers should project `eln_entry_id`, `eln_entry_url`, `eln_entry_provider`, and
  `eln_entry_provider_id`, alongside the existing array-valued `eln_entry` display ID.
  Entry URLs and provider-scoped IDs enable joins across notebook systems and tenants.
  The [specification](spec/profile.md#consumer-requirements) defines source fields,
  fallbacks, missing values and multi-entry handling. The [full example](0.3/example1/ro-crate-metadata.json)
  includes the entry and provider fields.
- **Detached S3 crates ([#4](https://github.com/quiltdata/quilt-ro-crate-profile/issues/4)).**
  An absolute S3 root `@id` ending in `/` supplies the base for relative `hasPart` IDs,
  so metadata can live outside a read-only data bucket. Relative paths remain package
  logical keys, and the existing containment and collision rules still apply. See the
  [detached example](0.3/example2/ro-crate-metadata.json), which also demonstrates a
  contextual parent link and an upstream MD5 checksum without adding JSON-LD keys.

Producers should declare the versioned `https://w3id.org/quilt/ro-crate/0.3` in root
`conformsTo`. The unversioned URI still points to 0.2. The spec includes explicit examples
of collisions between relative and absolute members.

**External validator compatibility:** `roc-validator` 0.13.0 accepts the S3 root but
rejects relative member IDs in detached mode, including with `--metadata-only`. The
committed detached example therefore fails its REQUIRED detached-member check. See
[tested results and reproduction commands](docs/validator-compatibility.md), including
an absolute-ID comparison that passes and its effect on package logical keys.

These are profile changes. Packaging Engine support for the new fields and S3 base rule
must be implemented separately; publishing this specification does not update consumers.
Benchling webhook 0.20.0 already links by `eln_entry`
([PR #402](https://github.com/quiltdata/benchling-webhook/pull/402)); using the new ID/URL
keys for linking requires a further integration change. Published 0.1 and 0.2 artifacts
remain frozen, and the three existing term IRIs are unchanged.

## The three artifacts

A profile is three things, and RO-Crate 1.2 gives each a distinct job. Conflating them is
the usual mistake.

| Artifact | Role | Here |
|---|---|---|
| Profile description | Human-readable spec. The profile URI MUST resolve to this | [`0.3/index.html`](0.3/index.html), generated from [`spec/profile.md`](spec/profile.md) |
| Profile Crate | Machine-readable RO-Crate that *is* the profile. Defines the terms and names the artifacts and their roles | [`0.3/ro-crate-metadata.json`](0.3/ro-crate-metadata.json) |
| Conforming crate | A crate that *uses* the profile, via `conformsTo` on its root | [`0.3/example1/ro-crate-metadata.json`](0.3/example1/ro-crate-metadata.json) |

The Profile Crate is the one people skip, and skipping it has a concrete cost: the three
terms this profile defines would be referenced by conforming crates and defined nowhere. The
profile relies on the specification's rule that contextual entities declared in a Profile
Crate need not be repeated in each conforming crate — which only holds if the Profile Crate
exists.

## Layout

```
spec/profile.md            source of truth for the current version's specification
0.1/                       a published version, frozen
0.2/                       a published version, frozen
0.3/                       the current version
  index.html               generated specification        (role: specification)
  ro-crate-metadata.json   the Profile Crate
  ro-crate-metadata.jsonld content-type alias, generated
  example1/
    ro-crate-metadata.json conforming example              (role: example)
  example2/
    ro-crate-metadata.json detached S3 example             (role: example)
docs/
  ontology-iri-lookup.md   how to find an instrument class IRI
  publishing.md            how a profile gets published, and why it takes two repos
w3id/
  .htaccess                copy of ids/quilt/.htaccess as submitted upstream
  README.md                copy of ids/quilt/README.md as submitted upstream
build.sh                   regenerates index.html and the .jsonld alias
validate.py                structural checks; exits non-zero on failure
```

`w3id/` is kept byte-identical to `ids/quilt/` as most recently submitted upstream —
[perma-id/w3id.org#6749](https://github.com/perma-id/w3id.org/pull/6749), then
[#6751](https://github.com/perma-id/w3id.org/pull/6751) for 0.2, and
[#6964](https://github.com/perma-id/w3id.org/pull/6964) for 0.3 (submitted, awaiting merge).
Changing a redirect target means another pull request there.

## Complying with the profile

**If you produce crates**, the requirements come down to two things: list every file to
package in the root entity's `hasPart`, and, if you name the package, give a valid name.
The [producer requirements](spec/profile.md#producer-requirements) state the exact rules
for paths, directories, logical keys, ids and names. Everything else for producers is a
[recommendation](spec/profile.md#producer-recommendations). Follow it and a consumer can index
the crate's people, instrument and notebook entry for search; depart from it and the crate
is still packaged. Compare against
[`0.3/example1/ro-crate-metadata.json`](0.3/example1/ro-crate-metadata.json), which follows
every recommendation.

**If you consume crates**, the consumer requirements are normative too. A conforming
consumer packages exactly what `hasPart` lists, resolves the package name in a defined
order, preserves the graph verbatim, and keeps the instrument's timestamps on the package
entries. It rejects a crate only when it cannot package it as written, and never for
departing from a recommendation.

A conforming crate needs **no `@context` extension**. All three profile terms are used in
`propertyID` and `additionalType` positions, which take IRIs rather than introducing JSON-LD
keys, so a conforming crate parses correctly under stock RO-Crate tooling with nothing
silently dropped.

## Building and validating

```sh
python3 -m venv .venv && .venv/bin/pip install pyld requests markdown

# Regenerate the HTML specification, JSON-LD alias and root version index
PATH="$PWD/.venv/bin:$PATH" ./build.sh 0.3
.venv/bin/python validate.py    # structural checks (pass a version to check another)
```

`build.sh` needs `markdown_py` from
[python-markdown](https://python-markdown.github.io/). Run it after any edit to
`spec/profile.md`; `index.html` is generated and should never be edited directly.

`validate.py` fetches and caches the RO-Crate JSON-LD context on first run. Set
`ROCRATE_CONTEXT` to a local file to run offline. It checks JSON-LD expansion with no term
dropped, the Profile Crate's structural requirements, resource descriptors and their roles,
term definitions agreeing with the term set in both directions, the base specification's
required root properties on each example, and the `.jsonld` alias being present and current.

It does **not** check arbitrary crates against the profile; no SHACL shape exists yet.
[`roc-validator`](https://github.com/crs4/rocrate-validator) covers the base specification
layer today.

## Publishing

Publishing a profile takes two repositories: this one, served over GitHub Pages, and a pull
request to [`perma-id/w3id.org`](https://github.com/perma-id/w3id.org) for the permanent
URI. Content negotiation has to live in the w3id rules because GitHub Pages cannot
negotiate — it only maps file extensions to content types.

See [`docs/publishing.md`](docs/publishing.md) for the full sequence and the reasoning.

Current state:

- [x] GitHub Pages enabled, serving at <https://quiltdata.github.io/quilt-ro-crate-profile/>
- [x] `https://w3id.org/quilt/ro-crate` registered ([perma-id/w3id.org#6749](https://github.com/perma-id/w3id.org/pull/6749), merged)
- [x] `https://w3id.org/quilt/ro-crate/0.2` resolving (versioned rules route any `MAJOR.MINOR`)
- [x] Unversioned URI moved to 0.2: [perma-id/w3id.org#6751](https://github.com/perma-id/w3id.org/pull/6751)
  merged September 25, 2026. The local snapshot was synchronized in
  [#2](https://github.com/quiltdata/quilt-ro-crate-profile/pull/2).
- [x] Publish 0.3: [#5](https://github.com/quiltdata/quilt-ro-crate-profile/pull/5) merged;
  verified Pages serves `/0.3/` and its JSON/JSON-LD artifacts, and the versioned w3id URI resolves.
- [ ] Repoint the unversioned URI from 0.2 to 0.3: submitted as
  [perma-id/w3id.org#6964](https://github.com/perma-id/w3id.org/pull/6964), awaiting merge.
  `w3id/` matches that submission; the live unversioned URI still points to 0.2.
- [x] Registry submission for 0.1 and 0.2 merged:
  [eScienceLab/RO-Crate-Profile-Portal#61](https://github.com/eScienceLab/RO-Crate-Profile-Portal/pull/61),
  merged October 21, 2026.
- [ ] Add 0.3 to the registry: submitted as
  [eScienceLab/RO-Crate-Profile-Portal#67](https://github.com/eScienceLab/RO-Crate-Profile-Portal/pull/67),
  awaiting merge. The versioned URI passes the registry content-type and RDF Profile checks.
- [ ] SHACL shape added under the `validation` role
- [x] Maintainer contact filled in, in [`w3id/README.md`](w3id/README.md) and the `.htaccess`

Pages serves the content types the w3id rules depend on. Verified for 0.3 on October 23, 2026:

| URL | Content-Type |
|---|---|
| [`/0.3/`](https://quiltdata.github.io/quilt-ro-crate-profile/0.3/) | `text/html; charset=utf-8` |
| [`/0.3/ro-crate-metadata.json`](https://quiltdata.github.io/quilt-ro-crate-profile/0.3/ro-crate-metadata.json) | `application/json; charset=utf-8` |
| [`/0.3/ro-crate-metadata.jsonld`](https://quiltdata.github.io/quilt-ro-crate-profile/0.3/ro-crate-metadata.jsonld) | `application/ld+json` |

This is why the `.jsonld` alias exists, and why the w3id rules negotiate to it rather than to
the `.json` the RO-Crate specification requires as a filename.

The permanent URI resolves with content negotiation. Verified live:

```
https://w3id.org/quilt/ro-crate
  Accept: text/html           -> 200 text/html         (the specification)
  Accept: application/ld+json -> 200 application/ld+json (the Profile Crate)
```

Term IRIs such as <https://w3id.org/quilt/ro-crate#packageName> resolve to the
specification page and scroll to the definition.

## Contributing

Issues and pull requests welcome. Two rules that keep the artifacts consistent:

- Edit `spec/profile.md`, never a generated `index.html`. Run `./build.sh` for the current
  version and commit both. A published version's directory is frozen; `spec/profile.md`
  describes only the current one.
- Run `validate.py` before opening a pull request. It is meant to be usable as a CI gate.

Changes that add or remove a normative requirement need a version bump. Terms already
published must not be removed or re-pointed, per the
[RO-Crate guidance on evolving profile vocabularies](https://www.researchobject.org/ro-crate/specification/1.2/profiles.html).

## References

- [RO-Crate 1.3 specification](https://www.researchobject.org/ro-crate/specification/1.3/)
- [RO-Crate profiles](https://www.researchobject.org/ro-crate/specification/1.2/profiles.html)
- [Process Run Crate](https://www.researchobject.org/workflow-run-crate/profiles/process_run_crate/), the recommended companion profile
- [ELN file format](https://github.com/TheELNConsortium/TheELNFileFormat)
- [Quilt documentation](https://docs.quiltdata.com/) and [quiltdata/quilt](https://github.com/quiltdata/quilt)

## License

Specification text and code: [Apache License 2.0](LICENSE).
Metadata in the Profile Crate: [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).
