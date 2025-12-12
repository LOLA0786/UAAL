# Architecture (Mermaid)

```mermaid
flowchart LR
  AgentClients -->|UAS| UAAL[UAAL API]
  UAAL --> PolicyEngine
  UAAL --> DB[(Postgres)]
  UAAL --> Metrics[Prometheus]
  UAAL --> Webhooks
  UAAL --> Queue[Redis/Celery]
  Queue --> Worker[Celery Worker]
  Worker --> Effectors[Effectors (Calendar/Email/Stripe)]
  Metrics --> Grafana

