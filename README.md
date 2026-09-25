# Quilt RO-Crate profile

An [RO-Crate](https://www.researchobject.org/ro-crate/) profile for crates that are
ingested into [Quilt](https://docs.quiltdata.com/) packages.

**Status: draft, version 0.1.0.** Published and resolvable at
<https://w3id.org/quilt/ro-crate>.

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

## The three artifacts

A profile is three things, and RO-Crate 1.2 gives each a distinct job. Conflating them is
the usual mistake.

| Artifact | Role | Here |
|---|---|---|
| Profile description | Human-readable spec. The profile URI MUST resolve to this | [`0.1/index.html`](0.1/index.html), generated from [`spec/profile.md`](spec/profile.md) |
| Profile Crate | Machine-readable RO-Crate that *is* the profile. Defines the terms and names the artifacts and their roles | [`0.1/ro-crate-metadata.json`](0.1/ro-crate-metadata.json) |
| Conforming crate | A crate that *uses* the profile, via `conformsTo` on its root | [`0.1/example1/ro-crate-metadata.json`](0.1/example1/ro-crate-metadata.json) |

The Profile Crate is the one people skip, and skipping it has a concrete cost: the three
terms this profile defines would be referenced by conforming crates and defined nowhere. The
profile relies on the specification's rule that contextual entities declared in a Profile
Crate need not be repeated in each conforming crate — which only holds if the Profile Crate
exists.

## Layout

```
spec/profile.md            source of truth for the specification
0.1/
  index.html               generated specification        (role: specification)
  ro-crate-metadata.json   the Profile Crate
  ro-crate-metadata.jsonld content-type alias, generated
  example1/
    ro-crate-metadata.json conforming example              (role: example)
docs/
  ontology-iri-lookup.md   how to find an instrument class IRI
  publishing.md            how a profile gets published, and why it takes two repos
w3id/
  .htaccess                copy of ids/quilt/.htaccess as submitted upstream
  README.md                copy of ids/quilt/README.md as submitted upstream
build.sh                   regenerates index.html and the .jsonld alias
validate.py                structural checks; exits non-zero on failure
```

`w3id/` is kept byte-identical to the files in
[perma-id/w3id.org#6749](https://github.com/perma-id/w3id.org/pull/6749) so the two cannot
drift. Changing a redirect target means another pull request there.

## Complying with the profile

**If you produce crates**, the requirements come down to two things: list every file to
package in the root entity's `hasPart`, and, if you name the package, give a valid name.
The [producer requirements](spec/profile.md#producer-requirements) state the exact rules
for paths, directories, logical keys, ids and names. Everything else for producers is a
[recommendation](spec/profile.md#producer-recommendations). Follow it and a consumer can index
the crate's people, instrument and notebook entry for search; depart from it and the crate
is still packaged. Compare against
[`0.1/example1/ro-crate-metadata.json`](0.1/example1/ro-crate-metadata.json), which follows
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

./build.sh 0.1                  # regenerate index.html and the .jsonld alias
.venv/bin/python validate.py    # structural checks
```

`build.sh` needs `markdown_py` from
[python-markdown](https://python-markdown.github.io/). Run it after any edit to
`spec/profile.md`; `index.html` is generated and should never be edited directly.

`validate.py` fetches and caches the RO-Crate JSON-LD context on first run. Set
`ROCRATE_CONTEXT` to a local file to run offline. It checks JSON-LD expansion with no term
dropped, the Profile Crate's structural requirements, resource descriptors and their roles,
term definitions agreeing with the term set in both directions, the base specification's
required root properties on the example, and the `.jsonld` alias being present and current.

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
- [ ] Listed in the [RO-Crate profiles registry](https://profiles.ro-crate.org/): submitted as
  [eScienceLab/RO-Crate-Profile-Portal#61](https://github.com/eScienceLab/RO-Crate-Profile-Portal/pull/61), awaiting review
- [ ] SHACL shape added under the `validation` role
- [x] Maintainer contact filled in, in [`w3id/README.md`](w3id/README.md) and the `.htaccess`

Pages serves the content types the w3id rules depend on. Verified against the live site:

| URL | Content-Type |
|---|---|
| [`/0.1/`](https://quiltdata.github.io/quilt-ro-crate-profile/0.1/) | `text/html; charset=utf-8` |
| [`/0.1/ro-crate-metadata.json`](https://quiltdata.github.io/quilt-ro-crate-profile/0.1/ro-crate-metadata.json) | `application/json; charset=utf-8` |
| [`/0.1/ro-crate-metadata.jsonld`](https://quiltdata.github.io/quilt-ro-crate-profile/0.1/ro-crate-metadata.jsonld) | `application/ld+json` |

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

- Edit `spec/profile.md`, never `0.1/index.html`. Run `./build.sh` and commit both.
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
