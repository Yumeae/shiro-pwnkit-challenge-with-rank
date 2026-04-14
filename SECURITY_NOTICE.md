# Security Notice — Intentionally Vulnerable Application

> **⚠ WARNING: This repository contains software that is deliberately
> insecure. It must only be deployed in a fully isolated environment.**

---

## Purpose

This project is a **Capture-The-Flag (CTF) challenge** platform.
The application is **intentionally vulnerable** to two specific CVEs as the
challenge objectives.  The vulnerable dependencies are not mistakes — they
are the challenge itself.

---

## Intentionally Vulnerable Dependencies

### 1. `org.apache.shiro:shiro-spring` — pinned to `1.2.4`

| Attribute | Detail |
|-----------|--------|
| **CVE** | CVE-2016-4437 |
| **Vulnerability** | Apache Shiro ≤ 1.2.4 ships with a **hardcoded AES-128-CBC key** (`kPH+bIxk5D2deZiIxcaaaA==`) used to encrypt the `rememberMe` cookie. An attacker with network access can forge a malicious cookie containing a serialized Java payload and achieve **Remote Code Execution**. |
| **Why kept** | This IS Stage 1 of the challenge. Upgrading to 1.2.5+ (random key) or 1.7.1 (auth-bypass fix) would remove the entire attack surface. |
| **Patched upstream** | ≥ 1.2.5 (key randomisation), ≥ 1.7.1 (auth-bypass fixes) |

### 2. `commons-collections:commons-collections` — pinned to `3.2.1`

| Attribute | Detail |
|-----------|--------|
| **CVEs** | CVE-2015-6420, CVE-2015-7501 |
| **Vulnerability** | The `InvokerTransformer` gadget chain in Commons Collections ≤ 3.2.1 enables arbitrary code execution when a malicious object graph is deserialized. This is the **gadget chain** used to weaponize the Shiro rememberMe RCE. |
| **Why kept** | Without this gadget chain the Shiro cookie payload cannot execute commands. Upgrading to 3.2.2 (serialisation filter) or 4.1 breaks the exploit. |
| **Patched upstream** | ≥ 3.2.2, ≥ 4.1 |

---

## Isolation Requirements

Because this application is deliberately exploitable, **it must never be
reachable from untrusted networks**.  Minimum isolation checklist:

- [ ] Run exclusively inside Docker (provided `docker-compose.yml`)
- [ ] Bind challenge port `8080` to `127.0.0.1` or a private/VPN network only
- [ ] Do **not** expose to the public internet
- [ ] Use a dedicated, disposable VM or cloud instance
- [ ] Apply network-level firewall rules to restrict access to authorised
      participants only
- [ ] Destroy the environment after the CTF event ends

---

## Scope

The vulnerabilities described above exist **by design** within the
`challenge/` Docker container.  The `leaderboard/` service contains no
intentionally vulnerable code; its dependencies should be kept up to date.

---

## Reporting Real Bugs

If you discover a **non-intentional** security issue (e.g. a vulnerability in
the leaderboard service or the Docker configuration that could allow container
escape), please open a GitHub issue labelled `security`.
