
# User Stories: Activity Record Feature

1. As a user, I want each task creation event to be recorded with the task title and timestamp, so I can verify when work items were added.
   - Acceptance criteria:
     - A new activity record is created when a task is created.
     - The record includes task title, action type "created", and timestamp.
     - The activity list displays the new record immediately after task creation.

2. As a user, I want task update events to be recorded whenever a task’s title, description, or status changes, so I can see what was modified.
   - Acceptance criteria:
     - An activity record is created for task updates.
     - The record includes the changed fields, previous value, new value, and timestamp.
     - If only status changes, the record indicates the status transition clearly.

3. As a user, I want task deletion events to be recorded in the activity log, so I can track when tasks were removed.
   - Acceptance criteria:
     - A deletion activity record is created when a task is deleted.
     - The record includes the deleted task title and deletion timestamp.
     - The activity log retains the deletion event after the task is removed.

4. As a user, I want the activity record history to display recent events in reverse chronological order, so I can review the latest changes first.
   - Acceptance criteria:
     - Activity records are ordered newest first.
     - Each displayed item shows action type, task title, and timestamp.
     - The activity view is updated automatically after each relevant task action.

AI assumption corrected: It was previously assumed that activity tracking only required a summary note; this was corrected to require specific create, update, delete, and status-change event details.


# User Stories: Tag Feature

1. As a user, I want to add one or more tags to a task when creating or editing it, so I can categorize tasks by topic or priority.
   - Acceptance criteria:
     - Tags can be entered during task creation and editing.
     - Saved tasks display the selected tags on the task card.
     - Tags remain associated with the task after saving.

2. As a user, I want tags to be entered as a comma-separated list and normalized by trimming whitespace, so my tags stay consistent.
   - Acceptance criteria:
     - Input accepts comma-separated tag values.
     - Tags are trimmed of whitespace before saving.
     - Empty tag entries are rejected and do not create blank tags.

3. As a user, I want the system to enforce a maximum number of tags per task, so I can keep tagging manageable.
   - Acceptance criteria:
     - The app enforces a defined maximum tag count (for example, 5 tags).
     - The user receives feedback if they attempt to exceed the limit.
     - Existing valid tags are still saved when the limit is reached.

4. As a user, I want tags to be displayed as distinct chips on each task card, so I can visually scan the task categories quickly.
   - Acceptance criteria:
     - Tags appear as chips or badges on task cards.
     - Each tag chip is clearly separated from task text.
     - The task card remains readable with multiple tags.

5. As a user, I want to filter tasks by tag name, so I can find all tasks with the same category.
   - Acceptance criteria:
     - A tag filter option is available in the task list or board.
     - Selecting a tag shows only tasks with that tag.
     - Clearing the filter returns the full task list.

AI assumption corrected: It was previously assumed tags were stored as raw text without validation; this was corrected to require normalized input and blank-value rejection to keep tag data clean.
