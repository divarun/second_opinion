"""
Failure Patterns Library
Curated collection of distributed systems failure patterns
"""
from app.models import FailurePattern, PatternCategory


# Define all failure patterns
PATTERNS = [
    FailurePattern(
        id="thundering_herd",
        name="Thundering Herd Amplification",
        description="Cascading load spikes from coordinated retries or cache invalidation",
        category=PatternCategory.LOAD,
        indicators=[
            "cache expiration",
            "synchronized retries",
            "periodic background jobs",
            "cache warming",
            "scheduled tasks",
            "TTL expiration"
        ],
        why_easy_to_miss="Appears benign in single-instance testing; only manifests at scale when many clients coordinate"
    ),

    FailurePattern(
        id="hidden_sync_dependency",
        name="Hidden Synchronous Dependency",
        description="Blocking calls in critical paths that aren't obvious from design docs",
        category=PatternCategory.DEPENDENCY,
        indicators=[
            "synchronous call",
            "blocking operation",
            "wait for response",
            "sequential processing",
            "must complete before",
            "requires confirmation"
        ],
        why_easy_to_miss="Libraries and SDKs often hide synchronous behavior; design docs focus on happy path"
    ),

    FailurePattern(
        id="load_shedding_blindspot",
        name="Load Shedding Blind Spot",
        description="Missing circuit breakers or backpressure mechanisms",
        category=PatternCategory.LOAD,
        indicators=[
            "no rate limiting",
            "unbounded queue",
            "accept all requests",
            "no backpressure",
            "no circuit breaker",
            "missing timeout"
        ],
        why_easy_to_miss="Systems appear to handle load until they suddenly don't; failure happens quickly"
    ),

    FailurePattern(
        id="retry_storm",
        name="Retry Storm",
        description="Exponential backoff failures causing request amplification",
        category=PatternCategory.LOAD,
        indicators=[
            "automatic retry",
            "retry logic",
            "exponential backoff",
            "client-side retry",
            "timeout and retry",
            "error handling retry"
        ],
        why_easy_to_miss="Retry logic is often added for resilience but can cause cascading failures"
    ),

    FailurePattern(
        id="partial_outage_inconsistency",
        name="Partial Outage Inconsistency",
        description="Split-brain scenarios and degraded state handling issues",
        category=PatternCategory.DISTRIBUTED,
        indicators=[
            "multi-region",
            "distributed consensus",
            "leader election",
            "partial availability",
            "network partition",
            "quorum"
        ],
        why_easy_to_miss="Partial failures are rarely tested; systems are tested as fully up or fully down"
    ),

    FailurePattern(
        id="cascading_timeout",
        name="Cascading Timeout",
        description="Chain reactions from upstream timeout propagation",
        category=PatternCategory.TIMING,
        indicators=[
            "timeout configuration",
            "upstream dependency",
            "service chain",
            "multi-hop request",
            "timeout propagation",
            "deadline"
        ],
        why_easy_to_miss="Each service looks fine individually; issues only appear in the full call chain"
    ),

    FailurePattern(
        id="resource_exhaustion",
        name="Resource Exhaustion",
        description="Memory, connection pool, or CPU saturation patterns",
        category=PatternCategory.RESOURCE,
        indicators=[
            "connection pool",
            "memory allocation",
            "file descriptor",
            "thread pool",
            "buffer size",
            "resource limit"
        ],
        why_easy_to_miss="Resource limits are often configuration details overlooked in design reviews"
    ),

    FailurePattern(
        id="silent_data_loss",
        name="Silent Data Loss",
        description="Data loss scenarios without clear error signals",
        category=PatternCategory.DATA,
        indicators=[
            "eventual consistency",
            "async writes",
            "fire and forget",
            "best effort",
            "background sync",
            "deferred processing"
        ],
        why_easy_to_miss="Async operations appear successful immediately; loss only discovered later"
    ),

    FailurePattern(
        id="metadata_corruption",
        name="Metadata Corruption",
        description="Inconsistent metadata causing system-wide issues",
        category=PatternCategory.DATA,
        indicators=[
            "metadata store",
            "configuration service",
            "service registry",
            "schema registry",
            "central coordination",
            "shared state"
        ],
        why_easy_to_miss="Metadata is often assumed to be reliable; corruption has wide blast radius"
    ),

    FailurePattern(
        id="clock_skew",
        name="Clock Skew Issues",
        description="Time synchronization problems in distributed systems",
        category=PatternCategory.TIMING,
        indicators=[
            "timestamp comparison",
            "time-based ordering",
            "TTL calculation",
            "session expiration",
            "time-based validation",
            "clock synchronization"
        ],
        why_easy_to_miss="Clock differences are small and tests use single-machine timestamps"
    ),

    FailurePattern(
        id="unbounded_growth",
        name="Unbounded Growth",
        description="Data structures or queues that grow without bounds",
        category=PatternCategory.RESOURCE,
        indicators=[
            "append only",
            "accumulate",
            "queue without limit",
            "log retention",
            "history tracking",
            "no cleanup"
        ],
        why_easy_to_miss="Growth is gradual; problem appears months after deployment"
    ),

    FailurePattern(
        id="poison_message",
        name="Poison Message",
        description="Messages that repeatedly crash consumers",
        category=PatternCategory.DATA,
        indicators=[
            "message queue",
            "event processing",
            "deserialization",
            "message handling",
            "consumer processing",
            "retry queue"
        ],
        why_easy_to_miss="Appears as normal error handling until message blocks entire queue"
    ),

    FailurePattern(
        id="hotspot",
        name="Hotspot/Hot Shard",
        description="Uneven load distribution causing single-point bottlenecks",
        category=PatternCategory.LOAD,
        indicators=[
            "sharding",
            "partitioning",
            "hash distribution",
            "load balancing",
            "data distribution",
            "popular keys"
        ],
        why_easy_to_miss="Uniform distribution is assumed; real-world data is often skewed"
    ),

    FailurePattern(
        id="degraded_availability",
        name="Degraded but Not Dead",
        description="Services that are slow but not failing health checks",
        category=PatternCategory.DEPENDENCY,
        indicators=[
            "health check",
            "liveness probe",
            "readiness check",
            "degraded performance",
            "slow response",
            "partial functionality"
        ],
        why_easy_to_miss="Binary health checks (up/down) miss degraded states that still respond"
    ),

    FailurePattern(
        id="version_skew",
        name="Version Skew",
        description="Incompatibility between different versions during rolling deploys",
        category=PatternCategory.DISTRIBUTED,
        indicators=[
            "rolling deployment",
            "backwards compatibility",
            "API versioning",
            "schema migration",
            "gradual rollout",
            "version compatibility"
        ],
        why_easy_to_miss="Testing is done with uniform versions; mixed versions only appear during deploys"
    ),

    FailurePattern(
        id="coordination_overhead",
        name="Coordination Overhead",
        description="Excessive coordination causing performance degradation",
        category=PatternCategory.DISTRIBUTED,
        indicators=[
            "distributed lock",
            "consensus protocol",
            "coordination service",
            "global synchronization",
            "cross-shard transaction",
            "distributed transaction"
        ],
        why_easy_to_miss="Coordination looks cheap in tests; network latency compounds at scale"
    ),

    FailurePattern(
        id="state_explosion",
        name="State Machine Explosion",
        description="Unexpected state combinations causing undefined behavior",
        category=PatternCategory.DATA,
        indicators=[
            "state machine",
            "multiple states",
            "concurrent updates",
            "state transitions",
            "complex workflow",
            "state validation"
        ],
        why_easy_to_miss="Happy path state transitions are tested; edge case combinations are not"
    ),

    FailurePattern(
        id="single_point_of_failure",
        name="Single Point of Failure",
        description="A critical component with no redundancy whose failure causes total system outage",
        category=PatternCategory.DEPENDENCY,
        indicators=[
            "single node",
            "no replica",
            "no failover",
            "standalone",
            "primary only",
            "no redundancy",
            "single instance",
            "no backup"
        ],
        why_easy_to_miss="HA is often deferred as a 'phase 2' concern and never revisited; the SPOF is invisible until it fails in production"
    ),

    FailurePattern(
        id="fanout_amplification",
        name="Fan-out Amplification",
        description="A single request triggering O(n) downstream requests, causing load amplification",
        category=PatternCategory.LOAD,
        indicators=[
            "for each user",
            "notify all",
            "broadcast",
            "fan out",
            "scatter gather",
            "per subscriber",
            "expand to all",
            "iterate over all",
            "send to followers"
        ],
        why_easy_to_miss="The multiplication factor is hidden behind a loop; trivial at small scale but catastrophic as data grows"
    ),

    FailurePattern(
        id="dual_write_inconsistency",
        name="Dual Write Inconsistency",
        description="Writing to two stores without atomicity causes permanent divergence on partial failure",
        category=PatternCategory.DATA,
        indicators=[
            "write to cache",
            "update index",
            "invalidate cache after",
            "publish event after write",
            "sync to secondary",
            "write-through",
            "update search index",
            "two stores",
            "also write to"
        ],
        why_easy_to_miss="Each individual write looks safe; the failure window between the two writes is tiny but causes silent, permanent divergence"
    ),

    FailurePattern(
        id="missing_idempotency",
        name="Missing Idempotency",
        description="Operations added for retry resilience that are not safe to replay, causing duplicate side effects",
        category=PatternCategory.DATA,
        indicators=[
            "retry on failure",
            "at-least-once",
            "requeue on error",
            "idempotency key",
            "duplicate detection",
            "process again",
            "re-deliver",
            "compensating transaction"
        ],
        why_easy_to_miss="Retries are added for reliability without verifying the operation is safe to repeat; duplicate charges or sends only surface in edge cases"
    ),

    FailurePattern(
        id="noisy_neighbor",
        name="Noisy Neighbor",
        description="One tenant or service consuming disproportionate shared resources, starving others",
        category=PatternCategory.RESOURCE,
        indicators=[
            "shared database",
            "multi-tenant",
            "same cluster",
            "shared cache",
            "common infrastructure",
            "shared pool",
            "single namespace",
            "shared table",
            "co-located"
        ],
        why_easy_to_miss="Tenants behave uniformly in testing; one aggressive tenant or workload only emerges in production under real usage patterns"
    ),

    FailurePattern(
        id="bulkhead_absence",
        name="Bulkhead Absence",
        description="No failure isolation between subsystems; a slow dependency consumes shared resources and takes down unrelated functionality",
        category=PatternCategory.DEPENDENCY,
        indicators=[
            "shared thread pool",
            "shared connection pool",
            "same executor",
            "no isolation",
            "common worker pool",
            "blocking call",
            "shared request queue",
            "no bulkhead"
        ],
        why_easy_to_miss="Each subsystem tests fine in isolation; cross-contamination only appears when one dependency degrades under production load"
    ),

    FailurePattern(
        id="event_ordering_assumption",
        name="Event Ordering Assumption",
        description="System assumes events arrive in order but does not enforce it; out-of-order delivery causes incorrect state",
        category=PatternCategory.DISTRIBUTED,
        indicators=[
            "event stream",
            "message ordering",
            "consumer offset",
            "event replay",
            "at-least-once delivery",
            "partition rebalance",
            "sequence number",
            "ordered processing",
            "changelog"
        ],
        why_easy_to_miss="Ordered delivery is the common case in testing; out-of-order events only appear during partition rebalancing, consumer restarts, or multi-partition reads"
    ),
]


def get_all_patterns():
    """Return all available failure patterns"""
    return PATTERNS


def get_pattern_by_id(pattern_id: str):
    """Get a specific pattern by ID"""
    for pattern in PATTERNS:
        if pattern.id == pattern_id:
            return pattern
    return None


def get_patterns_by_category(category: PatternCategory):
    """Get all patterns in a category"""
    return [p for p in PATTERNS if p.category == category]