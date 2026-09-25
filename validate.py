"""Structural validation for the Quilt RO-Crate profile.

Checks the Profile Crate and its example against the RO-Crate requirements for profiles,
and checks that the two agree with each other. Stands in for the SHACL shape that the
specification lists as not yet written.

    python3 -m venv .venv && .venv/bin/pip install pyld requests
    .venv/bin/python validate.py [VERSION]

The RO-Crate JSON-LD context is fetched once and cached under .cache/. Set
ROCRATE_CONTEXT to a local file to run fully offline.

Exits non-zero on any failure, so it is usable as a pre-publish gate or in CI.
"""

import json, os, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
VERSION = sys.argv[1] if len(sys.argv) > 1 else "0.1"
BASE = os.path.join(HERE, VERSION)
CONTEXT_URL = "https://w3id.org/ro/crate/1.2/context"


def load_context():
    override = os.environ.get("ROCRATE_CONTEXT")
    if override:
        return json.load(open(override))
    cache_dir = os.path.join(HERE, ".cache")
    cache = os.path.join(cache_dir, "ro-crate-1.2-context.json")
    if not os.path.isfile(cache):
        os.makedirs(cache_dir, exist_ok=True)
        req = urllib.request.Request(
            CONTEXT_URL, headers={"Accept": "application/ld+json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        open(cache, "wb").write(data)
        print(f"fetched and cached {CONTEXT_URL}")
    return json.load(open(cache))


CTX = load_context()
ctx = CTX["@context"]

from pyld import jsonld  # noqa: E402  (imported after the context is available)

jsonld.set_document_loader(
    lambda url, o=None: {"contextUrl": None, "documentUrl": url, "document": CTX})


def ty(e):
    t = e.get("@type", [])
    return t if isinstance(t, list) else [t]


def load(rel):
    raw = open(os.path.join(BASE, rel), "rb").read()
    assert raw[:3] != b"\xef\xbb\xbf", f"{rel}: has a UTF-8 BOM"
    return json.loads(raw.decode("utf-8"))


fails = []
for rel, kind in [("ro-crate-metadata.json", "Profile Crate"),
                  ("example1/ro-crate-metadata.json", "conforming crate")]:
    doc = load(rel)
    g = doc["@graph"]
    keys, types = set(), set()

    def w(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "@type":
                    for t in (v if isinstance(v, list) else [v]):
                        types.add(t)
                elif not k.startswith("@"):
                    keys.add(k)
                w(v)
        elif isinstance(o, list):
            for i in o:
                w(i)
    w(g)

    exp = jsonld.expand(doc)
    # A term absent from the context is silently dropped during expansion. Prefixed
    # names such as rdfs:label resolve via the prefix, so they are excluded here.
    dk = sorted(k for k in keys if ctx.get(k) is None and ":" not in k)
    dt = sorted(t for t in types if ctx.get(t) is None and ":" not in t)
    by = {e["@id"]: e for e in g}
    root = by[by["ro-crate-metadata.json"]["about"]["@id"]]
    ids = [e["@id"] for e in g]
    dup = sorted({i for i in ids if ids.count(i) > 1})

    refs = set()

    def w3(o):
        if isinstance(o, dict):
            if set(o) == {"@id"}:
                refs.add(o["@id"])
            for v in o.values():
                w3(v)
        elif isinstance(o, list):
            for i in o:
                w3(i)
    w3(g)
    dang = sorted(r for r in refs if r not in by
                  and not r.startswith(("http://", "https://", "urn:")))
    nulls = sorted({k for e in g for k in e if e[k] is None})

    print(f"=== {kind}: {VERSION}/{rel}")
    print(f"  entities={len(g)} expanded={len(exp)} keys={len(keys)} types={len(types)}")
    for n, v in [("dropped keys", dk), ("dropped types", dt),
                 ("duplicate @ids", dup), ("dangling refs", dang), ("nulls", nulls)]:
        print(f"    {n:18} {v or 'none'}")
        if v:
            fails.append(f"{rel}: {n} {v}")

    if kind == "conforming crate":
        # The base specification requires these on the root data entity.
        miss = [p for p in ("name", "description", "datePublished", "license")
                if p not in root]
        print(f"    {'ok ' if not miss else 'FAIL'} root has the base-spec required "
              f"properties{'' if not miss else ' -- missing ' + str(miss)}")
        if miss:
            fails.append(f"{rel}: root missing {miss}")
        # Process Run Crate requires actions to be reachable from the root.
        ments = root.get("mentions", [])
        ments = {m["@id"] for m in (ments if isinstance(ments, list) else [ments])}
        acts = {e["@id"] for e in g if "CreateAction" in ty(e)}
        orphan = sorted(acts - ments)
        print(f"    {'ok ' if not orphan else 'FAIL'} every CreateAction is in root "
              f"mentions{'' if not orphan else ' -- ' + str(orphan)}")
        if orphan:
            fails.append(f"{rel}: actions not in mentions {orphan}")

    if kind == "Profile Crate":
        # RO-Crate 1.2 profiles: the Profile Crate root MUST declare Profile as an
        # additional @type and MUST reference the human-readable description via
        # hasPart; it SHOULD have an absolute URI @id, name, version and isProfileOf.
        checks = {
            "root @type includes Dataset": "Dataset" in ty(root),
            "root @type includes Profile": "Profile" in ty(root),
            "root @id is absolute": root["@id"].startswith("https://"),
            "root has name": "name" in root,
            "root has version": "version" in root,
            "root has isProfileOf": "isProfileOf" in root,
            "root identifier == @id": root.get("identifier") == root["@id"],
        }
        hp = {p["@id"] for p in root["hasPart"]}
        html = [e for e in g if e["@id"] in hp
                and e.get("encodingFormat") == "text/html"]
        checks["hasPart includes a text/html description"] = bool(html)
        if html:
            checks["that description file exists on disk"] = os.path.isfile(
                os.path.join(BASE, html[0]["@id"]))
        for rd in root["hasResource"]:
            e = by.get(rd["@id"])
            ok = (bool(e) and "ResourceDescriptor" in ty(e)
                  and "hasRole" in e and "hasArtifact" in e)
            checks[f"{rd['@id']} well-formed"] = ok
            if ok:
                checks[f"{rd['@id']} artifact in hasPart"] = (
                    e["hasArtifact"]["@id"] in hp)
        dts = [e for e in g if "DefinedTermSet" in ty(e)][0]
        declared = {t["@id"] for t in dts["hasDefinedTerm"]}
        present = {e["@id"] for e in g if "DefinedTerm" in ty(e)}
        checks["every declared term is defined"] = declared <= present
        checks["every defined term is declared"] = present <= declared
        for t in declared:
            checks[f"{t.rsplit('#')[-1]} has termCode+description"] = (
                "termCode" in by[t] and "description" in by[t])
        ex = by["example1/"]
        checks["example declares this profile"] = root["@id"] in {
            c["@id"] for c in ex["conformsTo"]}
        checks["example crate exists on disk"] = os.path.isfile(
            os.path.join(BASE, "example1/ro-crate-metadata.json"))
        print("  Profile Crate structural checks:")
        for k, v in checks.items():
            print(f"    {'ok ' if v else 'FAIL'} {k}")
            if not v:
                fails.append(f"{rel}: {k}")
    print()

pc = load("ro-crate-metadata.json")
ex = load("example1/ro-crate-metadata.json")
pcb = {e["@id"]: e for e in pc["@graph"]}
pc_root = pcb[pcb["ro-crate-metadata.json"]["about"]["@id"]]["@id"]
exb = {e["@id"]: e for e in ex["@graph"]}
exroot = exb[exb["ro-crate-metadata.json"]["about"]["@id"]]
exc = {c["@id"] for c in exroot["conformsTo"]}

print("=== cross-artifact")
print(f"  Profile Crate root URI  : {pc_root}")
print(f"  example root conformsTo : {sorted(exc)}")
linked = pc_root in exc
print(f"    {'ok ' if linked else 'FAIL'} example points back at the Profile Crate")
if not linked:
    fails.append("example does not reference the Profile Crate URI")

# Every profile term the example uses must be defined in the Profile Crate, since
# conforming crates rely on the Profile Crate for those definitions.
NS = "https://w3id.org/quilt/ro-crate#"
defined = {e["@id"] for e in pc["@graph"] if "DefinedTerm" in ty(e)}
used = set()


def wu(o):
    if isinstance(o, dict):
        for v in o.values():
            wu(v)
    elif isinstance(o, list):
        for i in o:
            wu(i)
    elif isinstance(o, str) and o.startswith(NS):
        used.add(o)


wu(ex["@graph"])
undef = sorted(used - defined)
print(f"  profile terms used      : {sorted(used) or 'none'}")
print(f"    {'ok ' if not undef else 'FAIL'} all defined in the Profile Crate"
      + (f" -- undefined: {undef}" if undef else ""))
if undef:
    fails.append(f"undefined terms used by the example: {undef}")

# GitHub Pages serves .json as application/json; a .jsonld alias is needed so a client
# asking for application/ld+json can be redirected to a correctly typed URL.
a = os.path.join(BASE, "ro-crate-metadata.json")
b = os.path.join(BASE, "ro-crate-metadata.jsonld")
alias_ok = os.path.isfile(b) and open(a, "rb").read() == open(b, "rb").read()
print(f"    {'ok ' if alias_ok else 'FAIL'} ro-crate-metadata.jsonld alias present "
      "and identical")
if not alias_ok:
    fails.append("missing or stale ro-crate-metadata.jsonld alias -- run ./build.sh")

print("\n" + ("PASS - all checks" if not fails
              else "FAIL:\n  " + "\n  ".join(fails)))
sys.exit(0 if not fails else 1)
