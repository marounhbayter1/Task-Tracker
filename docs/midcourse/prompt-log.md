# Prompt Log

## Activity Record Feature

1. Prompt: "Implement activity tracking for task create/update/delete/status change events in the backend, and expose a recent-activity endpoint for the frontend."
   - AI returned: a plan to append event records to the task store, include action type, timestamps, and changed fields; plus a lightweight API endpoint to return the latest activity.
   - Result: accepted the overall design, edited the wording to match the existing JSON-backed data model, and used the event record approach in the decision note.

2. Prompt: "Design a small activity panel that shows recent task events in reverse chronological order with clear labels for created, updated, deleted, and status changes."
   - AI returned: UI guidance for a compact activity panel, field layout suggestions, and ordering recommendations.
   - Result: accepted the UI direction, edited it to keep the panel minimal and consistent with the current frontend.

3. Weak prompt rewritten: "Add activity tracking."
   - Weak AI result: a generic description of logging without backend or frontend implementation specifics.
   - Stronger prompt: "Implement activity tracking by appending create, update, delete, and status-change event records to the existing JSON task store and expose them through a simple backend endpoint for a recent activity panel."
   - AI returned: a concrete architecture and step-by-step implementation plan.
   - Result: rejected the weak prompt output, accepted the stronger prompt output after rewriting.

## Tag Feature

1. Prompt: "Implement tags for tasks with normalization, validation, and a maximum tag count."
   - AI returned: a design that stores tags as string lists, trims whitespace, rejects blank tags, and enforces tag count limits.
   - Result: accepted the backend validation approach and used it in the tag user stories and ADR.

2. Prompt: "How should tags be displayed on task cards and how can tag filtering be supported?"
   - AI returned: suggestions to render tags as chips/badges and a filter UI that shows tasks matching a selected tag.
   - Result: accepted the display and filter guidance, editing it to match the current simple task card layout.

3. Prompt: "Compare inline tag handling versus a dedicated tag service in a small JSON-backed task app."
   - AI returned: two options, one minimal inline option and one reusable service-layer option, with pros/cons for each.
   - Result: accepted the reusable tag service option as the better long-term fit, and used that reasoning in the ADR decision.