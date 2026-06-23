# Security Policy

## Reporting a vulnerability

If you discover a security vulnerability in AIM, please report it **privately**.
Do not open a public issue.

Email the maintainer directly at **phuonghx.me@gmail.com** with:

- a description of the issue and its potential impact,
- steps to reproduce, and
- any relevant version information (`aim --version`), OS, and Python version.

You can expect an initial acknowledgement within a few days. We will work with
you to understand the issue, prepare a fix, and coordinate disclosure. Please
give us a reasonable amount of time to address the problem before any public
disclosure.

## Supported versions

Security fixes are provided for the latest released minor version.

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |
| Older   | :x:                |

We recommend always running the most recent release.

## Local dashboard

AIM ships a local web dashboard. By design it binds only to the loopback
interface (`127.0.0.1`) and is not exposed to your network. Access is gated by a
per-session token that is generated when the dashboard starts. Treat that token
as a secret and do not share dashboard URLs that contain it.

## Scope

AIM is a zero-dependency CLI that reads and writes files in your project and can
optionally sync with GitHub Issues/Projects. Reports about the CLI, the bundled
MCP server, the local dashboard, and the GitHub sync are all in scope.
