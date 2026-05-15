# Design Document: Real-Time Analytics Ingestion Pipeline

## Overview

We are building a centralized event ingestion pipeline to replace ad-hoc per-team logging. All product teams will publish behavioral events (clicks, purchases, searches, errors) to a shared Kafka cluster. A fleet of consumers will process these events and write to our analytics store (ClickHouse) for dashboards and experimentation. The pipeline must handle 50,000 events/second at steady state, with headroom for 3x spikes.

## Architecture

### Components

1. **Kafka Cluster**: Shared across all teams; events are partitioned by `user_id`
2. **Schema Registry**: Confluent Schema Registry enforcing Avro schemas per event type
3. **Consumer Fleet**: Stateless workers that read from Kafka, validate, transform, and write to ClickHouse
4. **ClickHouse**: Columnar store for analytics queries
5. **Dead Letter Storage**: S3 bucket for events that fail processing
6. **Metadata Database**: PostgreSQL storing team configurations, schema versions, and topic ownership

### Data Flow

1. Producers publish events as Avro-encoded messages to their assigned Kafka topic
2. Consumer fleet reads events in batches, decodes using Schema Registry
3. Each consumer applies team-specific transformation rules fetched from the Metadata Database
4. Transformed events are batch-inserted into ClickHouse
5. Events that fail transformation are written to S3 dead letter storage for manual review
6. Dashboards query ClickHouse directly; no caching layer

## Design Decisions

### Shared Kafka Cluster

Rather than provisioning per-team Kafka clusters, all teams share a single cluster. This reduces operational overhead and allows the infrastructure team to manage one system. Teams are allocated topic quotas on request.

### Partition by User ID

Events are partitioned by `user_id` so that all events for a given user land on the same partition. This makes it easy to reconstruct per-user event sequences for funnel analysis. Consumer processing assumes events for a user arrive in the order they were produced.

### Schema Evolution Strategy

Teams can evolve their Avro schemas by registering a new version in Schema Registry. The consumer fleet is updated in a rolling deploy — old and new consumer versions run simultaneously during the rollout window. Consumers that encounter an unknown schema version log a warning and skip the message.

### Dead Letter Handling

Events that fail Avro deserialization (e.g., corrupt payload, unknown fields from a new schema version) are written to S3 and removed from the consumer's in-flight batch. Processing continues with the remaining events. The ops team reviews the dead letter bucket weekly.

### Retention Policy

Raw Kafka events are retained for 7 days (Kafka default). ClickHouse stores processed events indefinitely — we never delete analytics data as it may be needed for future compliance audits or retrospective analysis.

### Metadata Database as Central Coordinator

All consumers fetch their transformation configuration from a single PostgreSQL instance at startup and refresh it every 60 seconds. This allows teams to update their transformation rules without redeploying consumers.

### Cross-Region Aggregation

The pipeline runs in three AWS regions (us-east-1, eu-west-1, ap-southeast-1). Regional ClickHouse clusters are queried independently; dashboards aggregate results client-side. If a regional cluster is slow or unreachable, the dashboard shows results from the available regions and labels the view as partial.

## Scale Expectations

- 50,000 events/second steady state; 150,000 events/second spike
- ~20 teams publishing events; top 3 teams account for 70% of volume
- Average event size: 1.2 KB
- Consumer fleet: 40 pods, autoscaling up to 120

## Dependencies

- Kafka (shared cluster, managed by infra team)
- Confluent Schema Registry (single instance, same cluster)
- ClickHouse (one cluster per region)
- PostgreSQL (metadata and transformation rules)
- S3 (dead letter storage)

## SLOs

- Events visible in dashboards within 60 seconds of production
- < 0.1% event loss under normal operations
- Pipeline available 99.9% of the time
- No hard SLO on dead-letter volume (reviewed manually)
