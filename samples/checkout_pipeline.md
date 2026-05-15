# Design Document: Checkout & Payment Processing Service

## Overview

We are replacing the monolithic checkout flow with a dedicated service that handles cart finalization, payment processing, inventory reservation, and order creation. The service must support 2,000 concurrent checkouts at peak (Black Friday) and integrate with our existing inventory, payments, and fulfillment systems.

## Architecture

### Components

1. **Checkout API**: REST API that accepts checkout requests from web and mobile clients
2. **Payment Processor**: Calls third-party payment gateway (Stripe) to charge the card
3. **Inventory Service**: Reserves stock before confirming the order
4. **Order Service**: Creates and persists the order record
5. **Notification Dispatcher**: Sends confirmation emails and triggers downstream systems
6. **PostgreSQL**: Source of truth for orders and inventory counts

### Checkout Flow

1. Client submits cart with payment details to Checkout API
2. API validates cart contents and pricing
3. Payment Processor charges the card via Stripe
4. On success, Inventory Service decrements stock in the database
5. Inventory cache (Redis) is invalidated and repopulated with updated counts
6. Order Service writes the order record to PostgreSQL
7. Notification Dispatcher fans out to: email service, fulfillment system, loyalty points engine, analytics pipeline, and warehouse management system
8. API returns order confirmation to the client

## Design Decisions

### Payment Retries

If the Stripe API call times out or returns a 5xx, we retry up to 3 times with a 2-second fixed delay. This ensures we don't lose a sale due to a transient network blip.

### Inventory Reservation via Sequential Writes

After the payment succeeds, we decrement the inventory count in PostgreSQL and then delete the Redis cache key so the next read repopulates it. We do not use a distributed transaction — instead we rely on the two writes completing in sequence. If the service restarts between the two writes, the inventory DB and cache will be reconciled on the next cache miss.

### Order State Machine

Orders move through the following states: `cart` → `payment_pending` → `payment_processing` → `payment_failed` | `payment_succeeded` → `inventory_reserved` | `inventory_failed` → `fulfillment_pending` → `shipped` → `delivered` → `return_requested` → `return_approved` | `return_denied` → `refund_pending` → `refunded` | `refund_failed`. Concurrent events (e.g., a return request arriving while a refund is processing) will be handled by checking the current state and rejecting invalid transitions.

### Fan-out on Order Confirmation

Once the order is confirmed, the Notification Dispatcher sends the event to all downstream consumers synchronously before returning the response to the client. This ensures downstream systems are up-to-date before we tell the customer their order is placed. Downstream systems currently include: email confirmation, fulfillment queue, loyalty points service, warehouse management, fraud analytics, and the data warehouse ETL.

### Inventory Lock via Database Row Lock

To prevent overselling during concurrent checkouts, we use `SELECT FOR UPDATE` on the inventory row when decrementing stock. This serializes all concurrent checkouts for the same SKU through a single lock.

## Scale Expectations

- 500 orders/minute normal; 2,000 orders/minute peak
- Average cart: 3 SKUs
- 80% of peak traffic concentrated on top 20 SKUs (seasonal items)
- Target checkout completion time: < 3 seconds p95

## Dependencies

- Stripe (payment gateway)
- PostgreSQL (orders, inventory)
- Redis (inventory cache)
- Email Service (internal)
- Fulfillment System (internal)
- Loyalty Points Service (internal)
- Warehouse Management System (internal, legacy — p95 latency ~800ms)
- Data Warehouse ETL (internal)

## SLOs

- 99.9% checkout API availability
- < 3s checkout end-to-end (p95)
- Zero lost payments (any payment charged must produce an order)
- Inventory never oversold by more than 0 units
