# REFACTOR-028: Evaluate Model Registry Necessity

## Problem Statement
The current codebase uses a model registry pattern to avoid circular imports between models and blueprints. This adds complexity and dual maintenance paths (registry and direct imports). For a hobby project, this may be unnecessary overhead.

## Implementation
- Assess whether the model registry is justified for this project size and architecture.
- Investigate if import restructuring or lazy imports can resolve circular dependencies more simply.
- Propose a plan to either remove the registry or document its necessity.

## Acceptance Criteria
- Written analysis in the task file with a clear recommendation.
- If removal is recommended, create a follow-up task for refactor/removal.
- If kept, document rationale in DOC-018.
