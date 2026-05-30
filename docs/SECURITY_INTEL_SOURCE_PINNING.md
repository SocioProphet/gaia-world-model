# Security-Intel Source Pinning

Status: draft v0.1

## Purpose

GAIA provides the source-pinning and provenance lane for public security-intelligence inputs used by SCOPE-D, Ontogenesis, Prophet Platform, Prophet Workspace, Memory Mesh, and ProCybernetica scenario work.

This lane records where public security-intel material came from, how it was classified, and what it is allowed to support. It does not promote public intelligence into local observation, attribution, authorization, or action.

## What this lane pins

The lane may pin:

- MITRE ATT&CK release and documentation sources;
- MITRE ATLAS release and documentation sources;
- vendor reports;
- public incident reports;
- advisories;
- regulatory or legal references;
- taxonomy references used by Ontogenesis alignment work;
- external reports cited by SCOPE-D adversarial scenarios.

## Boundary

A pinned public source is external evidence support only.

It is not:

- proof of local compromise;
- attribution;
- engagement authorization;
- runtime authority;
- procedure execution authority;
- claim promotion;
- memory writeback approval;
- production observation;
- permission to scan, probe, exploit, deliver payloads, or mutate state.

## Required metadata

A security-intel source pin should record:

- stable source ID;
- source class;
- title;
- publisher or maintainer;
- source URL;
- retrieval timestamp or intended retrieval timestamp;
- hash status;
- license/terms posture;
- allowed downstream uses;
- forbidden downstream uses;
- related scenario or ontology references;
- provenance notes.

## Storage posture

Small manifest records live in normal git.

Large copied artifacts, when allowed by terms and useful for reproducibility, should follow the normal GAIA Curation Vault storage policy. If terms or size make copying inappropriate, the pin may remain URL/hash/provenance-only.

## Downstream relationship

- SCOPE-D may reference pinned source IDs as external support for scenarios.
- Ontogenesis may reference pinned source IDs for generated import provenance.
- Prophet Platform may consume scenario references that cite GAIA source pins.
- Memory Mesh may carry scenario learning that references source pins, but durable writeback remains governed elsewhere.

## Acceptance rule

No downstream system may treat a GAIA security-intel source pin as sufficient authority, sufficient evidence, local attribution, or claim promotion by itself.
