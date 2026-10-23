# Validator compatibility for 0.3

Checked on 2026-10-23 with [`roc-validator` 0.13.0](https://github.com/crs4/rocrate-validator),
the `ro-crate-1.2` profile, REQUIRED severity, metadata-only validation and explicit detached
packaging mode. No individual checks were suppressed. This tests base RO-Crate metadata;
it does not test this profile's packaging rules, S3 access, payload bytes or checksums.
The Quilt profile has no external-validator implementation yet. A versioned `conformsTo`
identifies the requested conventions; it does not install validation rules for them.

## Results

| Input | Result |
|---|---|
| Committed `0.3/example2/ro-crate-metadata.json` | 48 checks passed, 1 failed, 17 skipped; exit 1 |
| Copy with the two member IDs replaced everywhere by absolute S3 IDs | 49 checks passed, 0 failed, 17 skipped; exit 0 |

The committed example's only failed check is `ro-crate-1.2_21.1`, **Detached RO-Crate:
data entities MUST be web-based**. It emits two REQUIRED issues, for `wells/A1.fcs` and
`images/`: both are relative IDs. The S3 root itself does not produce an issue. The tool
does not resolve these members against the S3 root as this profile instructs a packaging
consumer to do. Metadata-only mode still enforces this detached-member rule.

The 17 skips are reported by the tool's metadata-only/detached settings and dependencies,
including availability and attached-root checks. An exit 0 here is not proof the source
objects exist or that the tool implements the Quilt S3-base rule.

For workflows that require an unmodified `roc-validator` 0.13.0 to pass, use absolute S3
member IDs throughout the graph. This changes packaging semantics: for example,
`wells/A1.fcs` retains that logical key as a relative member, whereas absolute
`s3://source-data/acquisitions/run-01/wells/A1.fcs` maps to `A1.fcs`. Check logical keys
and collisions before using this alternative. Keep relative members when those paths
are needed, and record the external validator incompatibility rather than presenting a
check-skipped run as full conformance.

## Parent links

Example2 links root `isPartOf` to a fragment-identified `CreativeWork` with the parent
collection's S3 location in `url`. This produces no root-linkage failures in either run.
A trial using `Dataset` instead produced REQUIRED failures in `ro-crate-1.2_10.0` and
`ro-crate-1.2_24.1`, even with a fragment ID. Although the
[base specification permits fragment-identified contextual Datasets](https://www.researchobject.org/ro-crate/specification/1.2/data-entities.html),
the `CreativeWork` pattern avoids those validator failures without adding the parent to
the packaging manifest.

## Reproduce

Use a separate environment so the validator's dependencies do not affect the build:

```sh
python3 -m venv /tmp/quilt-validator-0.13
/tmp/quilt-validator-0.13/bin/pip install roc-validator==0.13.0
/tmp/quilt-validator-0.13/bin/rocrate-validator validate \
  --profile-identifier ro-crate-1.2 --no-auto-profile \
  --metadata-only --packaging-mode detached --requirement-severity required \
  --cache-path .cache/roc-validator --output-format json \
  --output-file /tmp/roc-example2.json --no-paging \
  0.3/example2/ro-crate-metadata.json
```

The expected exit status for the committed example is **1**, with the two issues above.
To reproduce the absolute-ID comparison, generate a temporary copy (the original stays
unchanged):

```sh
python3 - <<'PY'
import json
from pathlib import Path

doc = json.loads(Path("0.3/example2/ro-crate-metadata.json").read_text())
base = "s3://source-data/acquisitions/run-01/"

def absolute_ids(value):
    if isinstance(value, dict):
        return {
            key: base + item if key == "@id" and item in ("wells/A1.fcs", "images/")
            else absolute_ids(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [absolute_ids(item) for item in value]
    return value

Path("/tmp/roc-example2-absolute.json").write_text(json.dumps(absolute_ids(doc)))
PY
/tmp/quilt-validator-0.13/bin/rocrate-validator validate \
  --profile-identifier ro-crate-1.2 --no-auto-profile \
  --metadata-only --packaging-mode detached --requirement-severity required \
  --cache-path .cache/roc-validator --output-format json \
  --output-file /tmp/roc-example2-absolute-report.json --no-paging \
  /tmp/roc-example2-absolute.json
```

The expected exit status for this comparison is **0**. No member data is downloaded.
