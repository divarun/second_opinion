"""
Failure Patterns Library
Curated collection of distributed systems failure patterns
"""
from models import FailurePattern, PatternCategory


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
    )
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