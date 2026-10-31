---
name: cybersec-workstation
description: Set up and manage a cybersecurity workstation on Termux/Samsung Fold 7 — install and run pentesting tools
triggers:
  - pentest setup
  - install security tools
  - cybersec tools
  - nmap
  - security workstation
  - pentest environment
---

# Cybersecurity Workstation (Samsung Fold 7)

Set up a full pentesting environment on Termux for Samsung Fold 7.

## Initial Setup

```bash
# Update Termux packages
pkg update && pkg upgrade

# Install essential tools
pkg install nmap sqlmap hydra netcat-openbsd nikto git python

# Optional: enable root tools (requires rooted device)
# These won't work without root but can still be installed
pkg install metasploit-framework  # large, ~500MB
```

## Core Tools install

```bash
# Reconnaissance
pkg install nmap           # Network scanner
pkg install dnsutils       # DNS tools (dig, nslookup)
pkg install whois          # WHOIS lookup

# Web attack
pkg install sqlmap         # SQL injection
pkg install nikto          # Web server scanner

# Network attack
pkg install hydra          # Password brute force
pkg install netcat-openbsd # Netcat
pkg install ncat           # Nmap's netcat (SSL support)

# Wireless (limited on Fold 7 without monitor mode)
pkg install aircrack-ng   # Wifi audit tools (monitor mode needs root)

# Forensics
pkg install binwalk        # Firmware analysis
pkg install exiftool       # Metadata extraction
pkg install forensics      # Forensic tools collection

# Python tools
pip install maigret        # Username OSINT
pip install subfinder      # Subdomain discovery (if available)
```

## Workspace Setup

```bash
# Create project structure
mkdir -p ~/projects/pentest/{recon,exploits,loot,reports,scans}
mkdir -p ~/projects/pentest/wordlists

# Use SecLists from Samsung storage if available
ln -sf "/storage/emulated/0/Samsung Fold 7 Tools/tools/seclists" ~/projects/pentest/wordlists/seclists

# Use linpeas if available
cp "/storage/emulated/0/Samsung Fold 7 Tools/tools/linpeas" ~/projects/pentest/ 2>/dev/null
```

## Common Workflows

### Network Reconnaissance

```bash
# Quick port scan
nmap -sV -T4 target_ip

# Full port scan (slower but thorough)
nmap -sV -p- -T4 target_ip

# Stealth scan
nmap -sS -T2 target_ip

# UDP scan
nmap -sU --top-ports 100 target_ip
```

### Web Application Testing

```bash
# Nikto web scan
nikto -h http://target

# SQL injection testing
sqlmap -u "http://target/page?id=1" --dbs

# Directory brute force (use gobuster if installed)
gobuster dir -u http://target -w ~/projects/pentest/wordlists/seclists/Discovery/Web-Content/common.txt
```

### Password Attacks

```bash
# SSH brute force
hydra -l root -P wordlist.txt ssh://target_ip

# HTTP form brute force
hydra -l admin -P wordlist.txt target_ip http-post-form "/login:user=^USER^&pass=^PASS^:F=incorrect"
```

## Samsung Fold 7 Notes

- Run intensive scans only when unfolded for better screen visibility
- Use DeX mode for multi-window pentesting workflow
- Battery drains fast during nmap scans — plug in
- ARM64 architecture — some x86-only tools won't work
- Wireless injection requires root + compatible WiFi chipset

## Pitfalls

- Many pentest tools need root for full functionality
- Termux netplan/WiFi control is limited
- `metasploit-framework` package is large and slow to install
- Some tools in pkg repos are outdated — check versions