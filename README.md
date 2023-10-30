# pyGPO

Python class for managing Group Policy Object (GPO) on Active Directory (AD) remotely.

## Description

pyGPO uses LDAP3 to authenticate to a domain controller remotely. After successfully authenticating to the domain controller, a user can get, link and unlink an GPO.

## Features

- NTLM authentication (password or NT:NTLM hash)
- Get links for a specific GPO
- Link a GPO to a object
- Unlink a GPO to a object

## Options

```bash
-h  --help              Show this screen
-dc --domaincontroller  Specify domain controller IP
-u  --username          Specify username
-p  --password          Specify password or NT:NTLM hash
-d  --domain            Specify domain
-g  --gpodn             Specify the GPO DN
-l  --link              Specify the target object to link
-ul --unlink            Specify the target object to unlink
```

## Examples

```bash
Get linked objects from GPO  pyGPO.py -dc 10.1.10.1 -d powercorp.local -u john -p 'John123' -g 'CN={2AADC2C9-C75F-45EF-A002-A22E1893FDB5},CN=POLICIES,CN=SYSTEM,DC=POWERCORP,DC=LOCAL'
Link GPO to object           pyGPO.py -dc 10.1.10.1 -d powercorp.local -u john -p 'John123' -g 'CN={2AADC2C9-C75F-45EF-A002-A22E1893FDB5},CN=POLICIES,CN=SYSTEM,DC=POWERCORP,DC=LOCAL' -l 'OU=SERVERS,DC=POWERCORP,DC=LOCAL'
Unlink GPO to object         pyGPO.py -dc 10.1.10.1 -d powercorp.local -u john -p 'John123' -g 'CN={2AADC2C9-C75F-45EF-A002-A22E1893FDB5},CN=POLICIES,CN=SYSTEM,DC=POWERCORP,DC=LOCAL' -ul 'OU=SERVERS,DC=POWERCORP,DC=LOCAL'
```

## Requirements

- ldap3

```bash
pip install ldap3
```

## Installation

```bash
git clone https://github.com/1ncendium/pyGPO.git
cd pyGPO
chmod +x pyGPO.py
./pyGPO.py
```
