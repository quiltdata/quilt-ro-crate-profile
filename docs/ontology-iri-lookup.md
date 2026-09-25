# Looking up ontology IRIs for `additionalType`

How to find the IRI for an instrument class, and verified IRIs for common laboratory
instruments.

## Why

The profile types an instrument as schema.org
[`IndividualProduct`](https://schema.org/IndividualProduct), which says "one identifiable
physical unit" but nothing about what kind. The instrument *class* goes in
[`additionalType`](https://schema.org/additionalType), which takes an IRI:

```json
{
  "@id": "https://example.org/instruments/INST-000123",
  "@type": "IndividualProduct",
  "additionalType": { "@id": "http://purl.obolibrary.org/obo/OBI_0400044" },
  "name": "Flow Cytometer 1"
}
```

This is the pattern the
[ELN file format](https://github.com/TheELNConsortium/TheELNFileFormat) recommends for the
same situation: `@type` for the schema.org class, `additionalType` for a more specific class
from an external vocabulary.

IRIs like `OBI_0400044` are unguessable by design — opaque numeric identifiers, not
mnemonics. Inventing one does not fail loudly. It produces a crate that validates, parses,
and quietly asserts something false. Hence a documented procedure rather than a convention.

## Which ontology

**[OBI](https://obofoundry.org/ontology/obi.html)**, the Ontology for Biomedical
Investigations, for instruments. It is the OBO Foundry ontology for investigation-related
entities, it has good coverage of laboratory hardware, and it is what the
[ISA and ARC RO-Crate profiles](https://nfdi4plants.github.io/arc-ro-crate-profile/) draw
on. Namespace: `http://purl.obolibrary.org/obo/`.

If OBI has no suitable term, in rough order of preference:
[EFO](https://www.ebi.ac.uk/efo/), [CHMO](https://obofoundry.org/ontology/chmo.html) for
chemical-methods detail, the wider [OBO Foundry](https://obofoundry.org/), then the
manufacturer's own product URL as a last resort. Do not mint a local term for something an
ontology already covers.

## Procedure

Browse at the [EBI Ontology Lookup Service](https://www.ebi.ac.uk/ols4/ontologies/obi). For
scripted or repeatable lookups, use the OLS4 API:

```bash
curl -s "https://www.ebi.ac.uk/ols4/api/search?q=flow%20cytometer&ontology=obi&rows=5" \
  | python3 -c "
import json,sys
for x in json.load(sys.stdin)['response']['docs']:
    print(f\"{x.get('obo_id','?'):18} {x.get('label','?'):45} {x.get('iri','')}\")
"
```

Then confirm the candidate. Two checks matter:

```bash
IRI='http://purl.obolibrary.org/obo/OBI_0400044'
curl -s "https://www.ebi.ac.uk/ols4/api/ontologies/obi/terms?iri=$(python3 -c \
  "import urllib.parse;print(urllib.parse.quote('$IRI',safe=''))")" \
  | python3 -c "
import json,sys
for t in json.load(sys.stdin)['_embedded']['terms']:
    print('label   :', t.get('label'))
    print('obsolete:', t.get('is_obsolete'))
    print('defn    :', (t.get('description') or ['n/a'])[0])
"
```

- **Read the definition.** Labels are ambiguous; definitions are not. `flow cytometer`,
  `flow cytometer analyzer` and `flow cytometer sorter` are three different terms, and the
  definition is how you tell which one you have.
- **Check `is_obsolete`.** OBO ontologies retain deprecated terms with `is_obsolete: true`
  rather than deleting them, so a search hit is not proof a term is current.

Pick the most specific term that is *certainly* true. `chromatography instrument` is better
than a wrong guess at a narrower subclass. Over-specifying is a factual error;
under-specifying is merely less useful.

## Recording the IRI

- Use the `http://purl.obolibrary.org/obo/OBI_nnnnnnn` form. Note `http`, not `https`, and
  an underscore, not a colon — that is the canonical IRI. `OBI:0400044` is the CURIE display
  form; in a crate it is not an IRI, so tools cannot resolve it.
- `additionalType` takes a reference object, `{"@id": "http://purl.obolibrary.org/obo/..."}`,
  not a bare string.
- A contextual entity for the term is OPTIONAL, but helps anyone reading the crate:

```json
{
  "@id": "http://purl.obolibrary.org/obo/OBI_0400044",
  "@type": "DefinedTerm",
  "name": "flow cytometer",
  "inDefinedTermSet": { "@id": "http://purl.obolibrary.org/obo/obi.owl" }
}
```

- No `@context` entry is needed. `additionalType` is already a schema.org property in the
  RO-Crate context and its value is an IRI, not a new JSON-LD key.

## Verified IRIs

Resolved via the OLS4 API on 2026-09-24. All confirmed `is_obsolete: false`.

| Instrument class | OBI ID | IRI |
|---|---|---|
| flow cytometer | OBI:0400044 | `http://purl.obolibrary.org/obo/OBI_0400044` |
| flow cytometer analyzer | OBI:0400008 | `http://purl.obolibrary.org/obo/OBI_0400008` |
| flow cytometer sorter | OBI:0400099 | `http://purl.obolibrary.org/obo/OBI_0400099` |
| HPLC instrument | OBI:0001057 | `http://purl.obolibrary.org/obo/OBI_0001057` |
| chromatography instrument | OBI:0000485 | `http://purl.obolibrary.org/obo/OBI_0000485` |
| microplate reader | OBI:0001058 | `http://purl.obolibrary.org/obo/OBI_0001058` |
| mass spectrometer | OBI:0000049 | `http://purl.obolibrary.org/obo/OBI_0000049` |
| DNA sequencer | OBI:0400103 | `http://purl.obolibrary.org/obo/OBI_0400103` |
| microscope | OBI:0400169 | `http://purl.obolibrary.org/obo/OBI_0400169` |
| centrifuge | OBI:0400106 | `http://purl.obolibrary.org/obo/OBI_0400106` |

Re-verify before relying on any of these in a new deployment; ontologies move.

## Who owns the mapping

The instrument inventory belongs to whoever operates the instruments, so the
instrument-to-IRI mapping does too. The profile treats `additionalType` as SHOULD, so a
missing or imprecise IRI does not prevent ingestion.

The practical approach is for the crate-writing script to keep a small
instrument-identifier-to-IRI table alongside whatever identifier mapping it already has, so
the IRI is emitted automatically rather than typed per run.

A consumer is not required to interpret these IRIs. They exist so that a future consumer, or
any other RO-Crate tool, can distinguish instrument classes without string-matching on
`name`.
