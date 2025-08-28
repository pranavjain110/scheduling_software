# CNC Workshop Production Planning Software - PRD

## 1. Project Overview

**Purpose:**
Develop a production planning software to manage CNC workshop operations, optimize machine utilization, and track part production in real-time. The software will handle day-wise scheduling, machine assignment, sub-batch production, and forecasting for multiple companies and parts.

**Scope:**

* Schedule parts for multiple companies.
* Track operations at sub-batch level.
* Handle machine eligibility and constraints.
* Provide day-wise slots for 2 shifts/day (4 slots/day).
* Allow manual adjustments, cascading delays, and early completions.
* Integrate monthly plans and 1–2 months of forecasts.
* Highlight scheduling conflicts (e.g., double-booked machines) while allowing temporary overlaps for flexible planning.

## 2. Users and Roles

| Role                | Permissions                                                                      |
| ------------------- | -------------------------------------------------------------------------------- |
| Production Manager  | Create/edit production schedule, assign machines, adjust slots, view dashboards. |
| Shop Floor Operator | Update operation status (in-progress/completed), view daily schedule.            |
| Admin               | Manage parts, operations, machines, companies, and system configuration.         |

## 3. Functional Requirements

### 3.1 Part & Operation Management

* Store company and part details.
* Define machining operations for each part:

  * OP sequence (OP10, OP20, …)
  * Machining time per piece
  * Loading/unloading time
  * Eligible machines for each operation
* Allow user to update eligible machines per part.

### 3.2 Machine Management

* Maintain a list of machines (CNC lathes, VMCs, robots).
* Track machine type and capacity.
* Track machine availability per slot/day.

### 3.3 Scheduling

* **Step 1: Add Monthly/Weekly Plan**

  * User selects **company**, **part number**, and enters **quantity** for current month (monthly/weekly) and next 2 months (forecast).
  * Each new schedule **supersedes the previous schedule** for the same company/part/month.

* Day-wise schedule with 2 shifts/day and 2 slots/shift → 4 slots/day.

* Assign parts to machines for a given slot.

* Support **sub-batch scheduling**: operations can overlap across sub-batches.

* Respect operation sequence per part, but allow staggered operations.

* **Double-booking allowed temporarily** for planning flexibility, but must be **highlighted clearly** (color-coded or tooltip).

* Provide **conflict resolution tools**:

  * Auto-suggest alternative slots or machines
  * Allow manual drag-and-drop to fix conflicts

* Automatically adjust dependent operations if a sub-batch is delayed.

* Allow manual expansion of slots or moving operations to different days.

### 3.4 Plan Import & Forecast

* Import customer monthly/weekly schedules.
* Import 1–2 month forecast for planning purposes.
* New schedule **replaces obsolete previous schedules** for the same company/part/month.
* Update existing plan without overriding completed operations.

### 3.5 Progress Tracking & Dashboard

* Track operation status: planned, in-progress, completed, delayed.
* Show day-wise progress for each part and operation.
* Indicate early/late completion and machine utilization.
* Provide Gantt-chart style visualization per machine/part/sub-batch.
* Highlight conflicts (e.g., double-booked machines) in dashboard view.

### 3.6 Reporting

* Generate reports:

  * Daily production report
  * Monthly plan vs actual production
  * Machine utilization
  * Delay/overdue operations
* Export schedules to Excel/CSV.

## 4. Non-Functional Requirements

* **Scalability:** Support 15–20 machines, 5–10 companies, and hundreds of parts.
* **Usability:** Spreadsheet-style interface, drag-and-drop slot assignment, easy sub-batch tracking.
* **Persistence:** Store all plans, schedules, and forecasts in SQLite.
* **Reliability:** Prevent unresolved double-booking at finalization; preserve historical data.
* **Extensibility:** Add new machines, parts, or companies without code changes.

## 5. Data Model (High-Level)

**Tables:**

* **Company** – `company_id`, `name`
* **Part** – `part_id`, `company_id`, `name`, `total_operations`
* **Operation** – `operation_id`, `part_id`, `sequence_number`, `machining_time`, `loading_time`
* **Machine** – `machine_id`, `name`, `type`
* **OperationMachine** – `operation_id`, `machine_id` (eligible machines)
* **MonthlyPlan** – `plan_id`, `part_id`, `company_id`, `month`, `planned_quantity`
* **ForecastPlan** – `forecast_id`, `part_id`, `company_id`, `month`, `week`, `forecasted_quantity`
* **ProductionSchedule** – `schedule_id`, `date`, `shift_number`, `slot_number`, `part_id`, `operation_id`, `machine_id`, `quantity_scheduled`, `sub_batch_id`, `status`

## 6. User Interface Requirements

* **Spreadsheet/Grid view:**

  * Rows = Parts
  * Columns = Days
  * Each cell = 4 slots/day
  * Dropdown for machine selection
  * Checkbox or slot selection for sub-batches
  * **Conflict highlighting:** Red or warning for double-booked slots

* **Gantt Chart view:**

  * Visualize operations per machine/sub-batch
  * Color-coded by status
  * Highlight overlapping or delayed operations

* **Dashboard:**

  * Machine utilization
  * Delayed/overdue operations
  * Forecasted vs actual production
  * Visual warning for conflicts

## 7. Workflow

1. **Add Monthly/Weekly Schedule:**

   * Select company and part
   * Enter quantity for current month (monthly/weekly) and next 2 months (forecast)
   * New schedules **supersede previous schedules** for same company/part/month

2. Add/update parts, operations, and machine eligibility.

3. Allocate operations to slots/machines.

4. Track sub-batch progress on the shop floor.

5. Adjust schedule in case of delays or early completion.

6. Identify and resolve double-booked slots or conflicts.

7. Integrate new customer plans and forecasts.

8. Generate reports and export if needed.

## 8. Technology Stack

* **Frontend:** React + AG-Grid / Handsontable
* **Backend:** Flask + SQLAlchemy (SQLite)
* **Database:** SQLite (single-shop setup, portable)
* **Optional:** OR-Tools for automated schedule optimization

## 9. Future Enhancements

* AI-based scheduling optimization using OR-Tools.
* Multi-factory integration.
* Mobile interface for shop floor operators.
* Automatic handling of machine breakdowns and dynamic reallocation.
