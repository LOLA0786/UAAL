#!/bin/bash
curl -X POST http://localhost:8000/admin/kill   -H "Authorization: Bearer ADMIN_KEY"   -d '{"agent":"pricing-agent"}'
