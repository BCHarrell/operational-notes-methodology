# client.com Info

**Primary Domain Controller:** 1.2.3.4 (dc01.client.com)

Compromised users
```
client\sql_dev
client\rick_astley
```
## Potential Attack Paths
- If we can get to SQL01.client.com, unconstrained delegation

## Undertaken Actions
* Share enum
* certipy
* bar
* baz

## General Notes
- Falcon on endpoints

# dev.client.com
**Primary Domain Controller:** 2.3.4.5 (dc02.dev.client.com)

Compromised users
```
client\sql_dev - foreign group membership
```
## Potential Attack Paths

## Undertaken Actions

## General Notes
- per client, no EDR except on servers