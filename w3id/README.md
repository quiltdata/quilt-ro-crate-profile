# Quilt permanent identifiers

Destination: a pull request to <https://github.com/perma-id/w3id.org> adding this file as
`ids/quilt/README.md`, alongside the `.htaccess` in this directory as
`ids/quilt/.htaccess`.

**Not yet submitted.** Until it is merged, `https://w3id.org/quilt/ro-crate` does not
resolve and every reference to it in this repository is forward-looking.

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

TODO: maintainer name and email before submitting the PR. The w3id maintainers ask for
contact details in either this file or an `.htaccess` comment.

## Notes

Term IRIs are intentionally unversioned while the profile URI is versioned, so that term
identifiers stay stable across profile revisions. This follows the pattern used by the
Common Provenance Model profile, whose terms sit at
`https://w3id.org/cpm/ro-crate#CPMProvenanceFile` while the profile itself versions.

## Checklist before opening the PR

- [ ] GitHub Pages enabled on the project repo, and the served URL confirmed
- [ ] `0.1/index.html` and `0.1/ro-crate-metadata.jsonld` reachable at that URL
- [ ] Maintainer contact filled in above and in the `.htaccess` header
- [ ] Rules tested against a local checkout of the w3id site
- [ ] Commits squashed, commit message naming the project rather than "Create .htaccess"
