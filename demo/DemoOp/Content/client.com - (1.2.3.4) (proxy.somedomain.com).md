---
openPorts:
  - "80"
  - "443"
services:
  - http
  - ssl
examined: true
finding: true
---

Assessment Tracker: [[DemoOp-Tracker]]
Related Host(s): [[]]

# General Notes

Really slow responses
# Actions Taken on Host
- Nuclei scan
- gobuster on main site and /dev
````ad-example
title: results
collapse: yes
```
gobuster results
```
````
* Credential stuffing on /login
# Findings
![[DemoOp-Findings#SQL Injection (client.com login)]]
