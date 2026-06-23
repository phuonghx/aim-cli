---
name: red-team-tactics
description: Organizes adversary-simulation work around the MITRE ATT&CK lifecycle -- recon, access, escalation, evasion, lateral movement, and impact -- with the goal of exposing detection gaps. It pairs each phase with objectives and emphasizes scope, minimal impact, and reporting. Use it when scoping a penetration test, running a red-team exercise, or assessing an attack surface against ATT&CK. Authorized engagements only.
---

# Red Team Tactics

Red teaming exists to make defenders better by safely rehearsing how a real attacker would behave. Everything below assumes written authorization, a defined scope, and an intent to report rather than to harm.

## The ATT&CK lifecycle

An engagement moves through recognizable stages. They are not strictly linear -- escalation and discovery often loop -- but each has a job:

| Stage | What it accomplishes |
|-------|----------------------|
| Reconnaissance | chart the attack surface |
| Initial access | establish the first foothold |
| Execution | run code on the target |
| Persistence | survive reboots and logouts |
| Privilege escalation | reach admin or root |
| Defense evasion | stay below detection thresholds |
| Credential access | collect usable credentials |
| Discovery | learn the internal layout |
| Lateral movement | reach additional hosts |
| Collection | gather the data of interest |
| Command & control | hold a reliable channel back |
| Exfiltration / impact | remove data or demonstrate effect |

## Reconnaissance

The first trade-off is passive versus active. Passive collection never touches the target -- low risk, limited yield. Active probing engages it directly -- richer data, higher chance of being noticed. Sequence accordingly: exhaust passive sources before generating traffic.

What is worth finding, and why:

| Finding | Why it matters |
|---------|----------------|
| Technology stack | shapes which exploits are viable |
| Staff and roles | feeds social-engineering pretexts |
| IP/network ranges | bounds the scanning scope |
| Vendors and partners | opens supply-chain angles |

## Gaining initial access

Choose the vector that fits the target and the rules of engagement:

| Vector | When it fits |
|--------|--------------|
| Phishing | a human target with reachable email |
| Public exploit | an exposed, unpatched service |
| Valid credentials | leaked, reused, or cracked logins |
| Supply chain | trusted third-party access exists |

## Escalating privileges

The checks differ by platform.

On **Windows**, look for unquoted service paths you can hijack, services with weak permissions you can modify, abusable token privileges (such as `SeDebugPrivilege`), and credentials sitting in memory or config.

On **Linux**, look for SUID binaries that run as a more privileged owner, sudo rules that permit unintended commands, kernel versions with known local exploits, and cron jobs pointing at scripts you can write to.

## Evading defenses

The aim is to operate without tripping alerts. Common techniques: living-off-the-land binaries (LOLBins) so legitimate tools do the work, obfuscating payloads, altering file timestamps, and clearing logs.

Operational discipline matters as much as technique -- act during business hours so activity blends in, shape traffic to look ordinary, keep channels encrypted, and avoid behavior that stands out from the baseline.

## Moving laterally

Movement usually rides on harvested credentials. The material you hold dictates the method:

| Material | Technique |
|----------|-----------|
| Cleartext password | standard authentication |
| NTLM hash | pass-the-hash |
| Kerberos ticket | pass-the-ticket |
| Certificate | certificate-based auth |

Typical paths between hosts: administrative shares, remote-access services (RDP, SSH, WinRM), and exploitation of internal-only services.

## Active Directory

AD is a frequent objective because it concentrates access. Recurring techniques and their targets:

| Technique | Target |
|-----------|--------|
| Kerberoasting | service-account passwords |
| AS-REP roasting | accounts lacking pre-authentication |
| DCSync | domain credential replication |
| Golden ticket | durable, forged domain access |

## Reporting

The deliverable is the point of the engagement. Reconstruct the full chain: how the foothold was obtained, which techniques followed, what was ultimately reached, and -- critically -- where detection should have fired but did not.

For every technique that succeeded, answer three questions: What control or alert should have caught this? Why did it fail to? What concrete change would catch it next time?

## Staying in bounds

**Always:** keep inside the agreed scope, hold impact to the minimum, raise the alarm immediately if you stumble onto a genuine live threat, and log every action you take.

**Never:** destroy production data, knock services offline unless that test is explicitly scoped, push past proof-of-concept, or retain sensitive data after the engagement.

## Habits that separate good from sloppy

| Sloppy | Disciplined |
|--------|-------------|
| Sprinting straight to exploitation | following the methodology in order |
| Causing collateral damage | minimizing footprint and impact |
| Treating the report as an afterthought | documenting throughout |
| Drifting past scope | staying inside agreed boundaries |

The purpose is always defensive: simulate the adversary so the organization can close the gaps before a real one finds them.
