# ADR: Activity/Event Tracking Feature

## Context
The new feature should record task lifecycle events such as create, update, delete, and status changes, and show a small activity panel that is easy to read. The current application is lightweight, with task data stored in a simple JSON-backed backend and a minimal frontend. The solution should add value without introducing unnecessary complexity.

## Option A: Embedded Activity Log in the Existing Task Store

### Summary
Store activity entries alongside the task data in the existing JSON-based storage model. Each task mutation appends a small event record, and the frontend reads the recent events from a lightweight API endpoint.

### How it works
- Add an activity/event list to the backend data model.
- On create, update, delete, or status change, append a new event such as:
  - task created
  - task updated
  - task deleted
  - status changed to InProgress/Done/ToDo
- Expose a simple endpoint to return recent activity for display.
- Render a compact activity panel in the UI showing the latest events in reverse chronological order.

### Pros
- Very small change to the current architecture.
- No extra database or service is required.
- Easy to understand and maintain for this project size.
- Keeps task history and task data close together.

### Cons
- Activity data is coupled to the main task store.
- Large event history may make the data file grow over time.
- Retrieval and filtering may become less clean if the volume increases.

### Best fit when
- The team wants the fastest path to a working feature.
- The app remains small and local-file based.
- Simplicity matters more than long-term scalability.


## Option B: Separate Event Store with a Thin Activity Service

### Summary
Introduce a small, separate event store and a simple activity service that records task events independently from the main task data. The task service continues to manage tasks, while the activity service handles event persistence and recent-event retrieval.

### How it works
- Create a lightweight activity module with a simple interface for recording events.
- Persist events in a separate JSON file or a minimal internal store.
- Keep the API thin: one endpoint to list recent activity, another to record events when task actions occur.
- The frontend uses the activity endpoint to display the activity panel.

### Pros
- Clear separation between task state and activity history.
- Easier to extend later with richer event filtering or analytics.
- Keeps the activity feature more modular and testable.

### Cons
- Slightly more structure than the current codebase needs.
- Adds another file or module to maintain.
- Slightly more work to wire up than Option A.

### Best fit when
- The team expects the activity panel to grow over time.
- A cleaner separation of concerns is valued.
- The project may later need more event-based features.

### Decision

I selected Option A because it matched the existing JSON-backed backend and kept the work within the scope of the course project. The implementation uses the current task storage model to append activity records and exposes them through the existing backend API for a simple recent-activity panel.

AI alternatives considered included a separate event store and a thin activity service, but those were rejected as too complex and out of scope for this learning project.


# ADR: Tag Feature

### Option A: Minimal Inline Tag Handling

### Summary
Keep tag handling simple by parsing and validating tags directly inside the existing task create and update flows. The backend stores tags as a list of strings on each task and the frontend uses the same list format for display and filtering.

### How it works
- Add an optional tags field to the task payload.
- Normalize tags inline in the task endpoints by trimming whitespace and removing empty values.
- Enforce simple limits such as maximum tag count and maximum tag length inside the same validation path.
- Display tags as chips on task cards and filter tasks by tag in the frontend.

### Pros
- Fastest implementation path.
- Minimal code changes and no extra abstraction.
- Fits the current lightweight architecture very well.

### Cons
- Validation logic is duplicated across create and update handlers if not carefully shared.
- Tag behavior is less reusable if the feature grows later.
- Harder to keep consistent over time as more tag-related rules are added.

### Best fit when
- The team wants the quickest way to ship the feature.
- The current project remains small and simple.
- No separate tag service abstraction is needed yet.

### Option B: Separate Tag Service Layer

### Summary
Introduce a small tag service layer that centralizes tag normalization, validation, and formatting. The task endpoints delegate to this service when tasks are created or updated, while the frontend continues to read and render tags as a list.

### How it works
- Create a dedicated tag helper or service module in the backend.
- Use it to normalize tags, filter empty values, and enforce optional tag-count and tag-length limits.
- Reuse the same service in both create and patch flows.
- Keep the task model and API payloads simple, while the tag logic remains centralized and reusable.

### Pros
- Cleaner separation of concerns.
- Easier to test and maintain.
- Better foundation if tag filtering, search, or analytics grow later.

### Cons
- Slightly more structure than the inline approach.
- Adds a small amount of code overhead.
- May feel heavier than necessary for this small app.

### Best fit when
- The team wants a maintainable structure from the start.
- Tag logic is expected to grow beyond a simple list field.
- A reusable backend abstraction is preferred over a quick inline implementation.

### Decision
I selected Option B because it provides a cleaner, more maintainable foundation for tag handling while still remaining lightweight.

The implementation centralizes normalization and validation in one place, which reduces duplication between create and update flows and makes the feature easier to extend later. It also keeps tag-specific rules isolated from the general task logic, so future improvements such as filtering, search, or tag analytics can be added without changing the core task endpoints.

AI alternatives considered included the minimal inline approach, but that was rejected because it would duplicate validation logic and make consistent tag behavior harder to maintain as the feature grows.