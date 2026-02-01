# Example Design Document: User Notification Service

## Overview
We're building a new notification service to send push notifications, emails, and SMS messages to users. The service will handle millions of notifications per day and integrate with existing user services.

## Architecture

### Components
1. **API Gateway**: Receives notification requests
2. **Queue Service**: Redis-based queue for async processing
3. **Worker Pool**: Processes notifications from queue
4. **Provider Integrations**: Third-party services (SendGrid, Twilio, FCM)
5. **User Service**: External service providing user preferences

### Flow
1. Client sends notification request to API Gateway
2. Gateway validates request and enqueues to Redis
3. Workers poll Redis queue continuously
4. Workers fetch user preferences from User Service
5. Workers send notification via appropriate provider
6. Results are logged to database

## Design Decisions

### Synchronous User Preference Lookup
Workers will synchronously call the User Service to fetch delivery preferences for each notification. This ensures we always have the latest user settings.

### No Circuit Breakers
Since we're using reliable cloud providers (AWS, Twilio), we don't need circuit breakers. The services have 99.9% uptime SLAs.

### Fixed Retry Logic
If a provider fails, we'll retry 3 times with 1-second delays between attempts. This should handle most transient failures.

### Single Redis Instance
We'll use a single Redis instance for the queue. Redis is fast and we don't expect more than 10,000 messages in the queue at any time.

### Cache Warming at Midnight
We'll warm the user preferences cache every night at midnight UTC to ensure good performance during the day.

### Background Job for Cleanup
A cron job runs every hour to clean up old notification records from the database.

## Scale Expectations
- 5 million notifications/day
- 500,000 active users
- Peak: 100 notifications/second

## Dependencies
- User Service (internal)
- Redis (single instance)
- SendGrid (email)
- Twilio (SMS)
- Firebase Cloud Messaging (push)
- PostgreSQL (notification logs)

## SLOs
- 99% of notifications delivered within 10 seconds
- 99.9% API availability
- <100ms API response time (p95)