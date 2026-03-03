# RBAC Matrix

| Role | EHR Access | Billing System | Admin Systems | Security Console | Medical Device Mgmt |
|------|------------|----------------|---------------|------------------|---------------------|
| Clinician | Read/Write Assigned Patients | None | None | None | None |
| Nurse | Read/Write Assigned Patients | None | None | None | Limited (approved tasks) |
| Billing | Demographic + Billing Only | Read/Write | None | None | None |
| IT Admin | None (break-glass only) | None | Full | Limited Admin | Full |
| Security Analyst | Read Logs Only | None | None | Full | None |
| Vendor | None by default | None | Time-bound approved access | None | Approved maintenance only |

Rules:
- Enforce MFA for all roles.
- All privileged actions require named accounts.
- Vendor access is time-boxed and approved per ticket.
