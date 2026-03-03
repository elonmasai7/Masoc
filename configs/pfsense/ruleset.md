# pfSense/OPNsense Baseline Rules

Apply top-to-bottom per interface.

## STAFF (VLAN10)
1. Allow STAFF_NET -> EHR_SERVERS TCP 443,8443
2. Allow STAFF_NET -> DNS resolver TCP/UDP 53
3. Allow STAFF_NET -> NTP server UDP 123
4. Deny STAFF_NET -> MEDICAL_NET any
5. Deny STAFF_NET -> MGMT_NET any (except approved jump host)
6. Deny STAFF_NET -> RFC1918_NETS any (implicit/explicit final deny)
7. Allow STAFF_NET -> any (internet via NAT)

## SERVERS (VLAN20)
1. Allow SERVERS_NET -> required update repos (FQDN alias)
2. Allow SERVERS_NET -> MGMT_HOSTS admin ports (22/3389/5985 as needed)
3. Deny SERVERS_NET -> GUEST_NET any
4. Deny SERVERS_NET -> STAFF_NET any (except explicit required app responses if state not tracked)

## MEDICAL (VLAN30)
1. Allow MEDICAL_NET -> CRITICAL_SERVERS required app ports only
2. Deny MEDICAL_NET -> STAFF_NET any
3. Deny MEDICAL_NET -> GUEST_NET any
4. Deny MEDICAL_NET -> internet any (unless vendor update exception)

## GUEST (VLAN40)
1. Deny GUEST_NET -> RFC1918_NETS any
2. Allow GUEST_NET -> any (internet only)

## MGMT (VLAN50)
1. Allow MGMT_NET -> all internal VLANs admin ports only
2. Allow MGMT_NET -> Wazuh/OpenVAS/WireGuard management ports
3. Deny MGMT_NET -> GUEST_NET any
