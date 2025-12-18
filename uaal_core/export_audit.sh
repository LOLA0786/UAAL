#!/bin/bash
curl http://localhost:8000/admin/export   -H "Authorization: Bearer ADMIN_KEY"   -o uaal_audit.json
