---
startDate:
endDate:
status:
opType:
---


# Quick Links:
[[OpName-Findings]]
*Any links to op logs, op folders, Jira tickets, etc.*

# Kickoff Notes

# General Notes

# To-Do list

- [ ]

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
