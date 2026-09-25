# Quilt RO-Crate profile

An [RO-Crate](https://www.researchobject.org/ro-crate/) profile for crates that are
ingested into [Quilt](https://docs.quiltdata.com/) packages.

**Status: draft, version 0.1.0.** The profile URI is not yet registered — see
[Publishing](#publishing) below.

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
  .htaccess                drafted for a PR to perma-id/w3id.org
  README.md                drafted for the same PR
build.sh                   regenerates index.html and the .jsonld alias
validate.py                structural checks; exits non-zero on failure
```

## Complying with the profile

**If you produce crates**, work through the producer requirements in
[`spec/profile.md`](spec/profile.md) and compare against
[`0.1/example1/ro-crate-metadata.json`](0.1/example1/ro-crate-metadata.json), which is a
complete conforming crate. The short version: declare `conformsTo` on the root entity, list
every file in `hasPart`, give people absolute identifiers, record acquisition as a
`CreateAction` reachable from `mentions`, and express anything domain-specific with
`variableMeasured` rather than inventing JSON keys.

**If you consume crates**, the consumer requirements are normative too. A conforming
consumer packages exactly what `hasPart` lists, resolves the package name in a defined
order, preserves the graph verbatim, keeps the instrument's timestamps on the package
entries, and rejects rather than partially ingests a crate that claims conformance and fails
it.

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

- [ ] GitHub Pages enabled and the served URL confirmed
- [ ] `https://w3id.org/quilt/ro-crate` registered via a PR to `perma-id/w3id.org`
- [ ] Listed in the [RO-Crate profiles registry](https://profiles.ro-crate.org/)
- [ ] SHACL shape added under the `validation` role
- [ ] Maintainer contact filled in, in [`w3id/README.md`](w3id/README.md) and the `.htaccess`

Until the first two are done, every `https://w3id.org/quilt/...` URI in this repository is
forward-looking and does not resolve.

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
