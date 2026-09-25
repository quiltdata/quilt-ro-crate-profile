# Quilt permanent identifiers

Destination: a pull request to <https://github.com/perma-id/w3id.org> adding this file as
`ids/quilt/README.md`, alongside the `.htaccess` in this directory as
`ids/quilt/.htaccess`.

Until that pull request is merged, `https://w3id.org/quilt/ro-crate` does not resolve and
every reference to it in this repository is forward-looking. The GitHub Pages URLs it
redirects to are live now.

## Namespace

`https://w3id.org/quilt/` is used by Quilt Data, Inc. for stable identifiers relating to
Quilt data packaging.

## Identifiers

| Identifier | Resolves to |
|---|---|
| `https://w3id.org/quilt/ro-crate` | Latest version of the Quilt RO-Crate profile |
| `https://w3id.org/quilt/ro-crate/0.1` | Version 0.1 of the profile |
| `https://w3id.org/quilt/ro-crate#<term>` | Term definitions, as anchors on the profile page |

Content negotiation: `application/ld+json` returns the Profile Crate; anything else
returns the HTML specification.

Source and hosting: <https://github.com/quiltdata/quilt-ro-crate-profile>, served via
GitHub Pages.

## Contact

Ernest Prabhakar <ernest@quilt.bio>, Quilt Data, Inc.

## Notes

Term IRIs are intentionally unversioned while the profile URI is versioned, so that term
identifiers stay stable across profile revisions. This follows the pattern used by the
Common Provenance Model profile, whose terms sit at
`https://w3id.org/cpm/ro-crate#CPMProvenanceFile` while the profile itself versions.

## Checklist before opening the PR

- [x] GitHub Pages enabled on the project repo, and the served URL confirmed
- [x] `0.1/index.html` and `0.1/ro-crate-metadata.jsonld` reachable at that URL, with
      `application/ld+json` returned for the latter
- [x] Maintainer contact filled in above and in the `.htaccess` header
- [x] Single commit, message naming the project rather than "Create .htaccess"
- [ ] Rules exercised against a local checkout of the w3id site (the maintainers ask for
      this; the rules here are modelled directly on `ids/ro/wfrun/process/.htaccess` but
      have not been run through Apache)
