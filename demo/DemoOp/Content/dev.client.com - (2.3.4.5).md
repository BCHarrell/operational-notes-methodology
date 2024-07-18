---
openPorts:
  - "22"
  - "80"
  - "443"
services:
  - ssh
  - http
  - ssl
examined: 
finding:
followUp:
---

Assessment Tracker: [[DemoOp-Tracker]]
Related Host(s): [[]]

# General Notes

# Actions Taken on Host
- SSH only supports PKI, no password
- 80 redirects to 443
- auth redirects to MSO
# Findings
