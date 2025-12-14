from billing.quotas import Quota
from billing.plans import PLANS

ORG_QUOTAS = {}

def enforce_quota(org):
    if org.id not in ORG_QUOTAS:
        ORG_QUOTAS[org.id] = Quota(PLANS[org.plan])
    ORG_QUOTAS[org.id].consume()
