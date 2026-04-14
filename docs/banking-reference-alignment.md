# Banking Reference Alignment

## Purpose

This note records the first external banking reference anchors for the GAIA banking-firm semantic seed.

The current banking-firm profile and domain manifests are seed artifacts for the SocioProphet banking twin.
They are **not** a claim of full external standard conformance.

## Reference anchors

### FIBO

FIBO is the Financial Industry Business Ontology maintained by EDM Council and standardized through OMG.
It is the primary ontology reference point for financial concepts, legal entities, instruments, loans, and related business semantics.

Within the banking-twin work, FIBO should be used as a reference ontology for:
- legal entity semantics
- financial instrument and obligation semantics
- loan and credit semantics
- contract and party role semantics
- reporting/risk terminology normalization

### BIAN

BIAN is the Banking Industry Architecture Network reference framework for banking interoperability,
service domains, and semantic APIs.

Within the banking-twin work, BIAN should be used as a reference architecture for:
- banking service-domain decomposition
- API and service boundary naming
- business capability and service interaction framing
- operational and coreless-banking service alignment

## Working rule

Use FIBO primarily for ontology and concept alignment.
Use BIAN primarily for service-domain and operational boundary alignment.

When the two overlap, prefer explicit mapping notes rather than silent conflation.

## Immediate next step

The next banking semantic tranche SHOULD:
1. annotate candidate domain overlaps with relevant FIBO areas,
2. annotate runtime/service candidates with relevant BIAN service-domain references,
3. record any mismatches as explicit divergence notes.
