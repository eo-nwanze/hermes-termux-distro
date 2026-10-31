---
name: domain
description: Domain name research, WHOIS lookups, DNS enumeration, and subdomain discovery from Termux/Android. Tools for reconnaissance and domain intelligence.
tags: [domain, dns, whois, subdomain, recon, termux, osint]
version: 1.0.0
---

# Domain Research on Termux/Android

## Overview
Tools and workflows for domain name research, DNS analysis, WHOIS lookups, and subdomain enumeration from Termux on Samsung A51.

## Installation

### Core DNS Tools
```bash
pkg update && pkg upgrade
pkg install dnsutils whois curl
```

### Go-Based Recon Tools
Install Go with `pkg install golang`, then build subfinder, amass, dnsx, and httpx from source using `go install`.

### Python DNS Libraries
Install dnspython and python-whois via pip for scriptable DNS and WHOIS queries.

## WHOIS Lookup

### Basic WHOIS
```bash
whois example.com

# Parse key fields
whois example.com | grep -E "(Registrant|Expiry|Name Server|Creation)"
```

### Python WHOIS Scripting
```python
import whois

def domain_info(domain):
    w = whois.whois(domain)
    return {
        "domain": domain,
        "registrar": w.registrar,
        "created": w.creation_date,
        "expires": w.expiration_date,
        "nameservers": w.name_servers,
        "status": w.status,
    }
```

## DNS Enumeration

### Record Type Queries
```bash
dig example.com A     # IPv4 addresses
dig example.com AAAA  # IPv6 addresses
dig example.com MX    # Mail servers
dig example.com NS    # Name servers
dig example.com TXT   # TXT records (SPF, DKIM)
dig example.com CNAME # Canonical names
dig example.com SOA   # Start of authority

# All records (may be refused on some servers)
dig example.com ANY

# Specify resolver
dig @8.8.8.8 example.com A
```

### Reverse DNS (IP to hostname)
Use `dig -x <IP_ADDRESS>` to perform reverse lookups.

## Subdomain Discovery

### Using Subfinder
After building subfinder with Go, run subdomain discovery against target domains. Output results to a file for further processing.

### Certificate Transparency Logs
Query crt.sh for certificate data associated with a domain. Parse the JSON output to extract unique subdomain names.

### DNS Brute Force Pattern
Iterate through common subdomain prefixes (www, mail, ftp, admin, api, dev, staging, test, blog) and check each with dig. Only print results that resolve.

## HTTP Probing
After discovering subdomains, probe each for live HTTP services using httpx. Extract status codes, page titles, and detected technologies.

## Domain Monitoring Workflow
1. Save WHOIS and DNS snapshots with timestamps
2. Periodically re-check and diff against previous snapshots
3. Alert on changes to DNS records, WHOIS data, or subdomain lists

## Pitfalls
- WHOIS rate limits: add delays between queries and use `--no-rdap` if needed
- DNS ANY queries often return REFUSED on modern servers — query specific record types
- DNS zone transfers (AXFR) rarely work on production domains
- Certificate Transparency logs may contain stale entries — always verify with DNS resolution
- Go tools need GOPATH and PATH configured in your shell profile
- Some DNS resolvers block mobile IP ranges — use explicit resolvers like 8.8.8.8