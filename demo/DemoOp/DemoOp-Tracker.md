---
startDate: 2024-01-01
endDate: 2024-01-15
status: complete
opType: external
---

**Quick Links:**
[OpLog](https://www.youtube.com/watch?v=dQw4w9WgXcQ)
[Box](https://www.youtube.com/watch?v=dQw4w9WgXcQ)
[Jira](https://www.youtube.com/watch?v=dQw4w9WgXcQ)

[[DemoOp-Findings]]

# Kickoff Notes
* Client wants me to avoid heavy scans during business hours
* Client wants a tech debrief with the larger engineering team

# General Notes
- Don't nmap scan 1.2.3.4

# To-Do list

- [ ] Resume nuclei scan (paused at client request)

## Host Trackers
```dataview
TABLE examined as "Completed"
FROM [[]]
SORT Completed asc
```

```dataview
TABLE privilegeLevel as "Privilege"
FROM [[]]
```

Follow-up:
```dataview
TABLE followUp as "Follow Up"
FROM [[]]
WHERE followUp
```

# Data Queries
Some example queries:

## Hosts with Findings

```dataview
TABLE finding as "Finding"
FROM [[]]
WHERE finding
```

## Services / Ports heading
These may or may not be helpful and are provided as examples. Requires the frontmatter (properties) to have been supplied.

**Single Service Query - Replace serviceName**

```dataview
LIST
FROM [[]]
WHERE icontains(services,"serviceName")
```

**Single Port Query - Replace portNum (example is port 80)**
```dataview
LIST
FROM [[]]
WHERE icontains(openPorts, "80")
```

Table for multiple ports/services
```dataview
TABLE services as "Services"
FROM [[]]
WHERE icontains(services, "serviceName") OR icontains(services, "serviceName")
```
