# Backend - CNC Workshop Production Planning Software

This is the Flask backend for the CNC Workshop Production Planning Software.

## Setup

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Run the application:
```bash
python run.py
```

The application will start on `http://127.0.0.1:5000`

## Database Models

The application implements the following SQLAlchemy models:

### Core Models

1. **Company** (`companies` table)
   - `company_id` (Primary Key)
   - `name`

2. **Part** (`parts` table)
   - `part_id` (Primary Key)
   - `company_id` (Foreign Key → companies.company_id)
   - `name`
   - `total_operations`

3. **Operation** (`operations` table)
   - `operation_id` (Primary Key)
   - `part_id` (Foreign Key → parts.part_id)
   - `sequence_number` (e.g., 10, 20, 30)
   - `machining_time` (minutes)
   - `loading_time` (minutes)

4. **Machine** (`machines` table)
   - `machine_id` (Primary Key)
   - `name`
   - `type` (e.g., "CNC Lathe", "VMC", "Robot")

### Association Tables

5. **OperationMachine** (`operation_machines` table)
   - `operation_id` (Foreign Key → operations.operation_id)
   - `machine_id` (Foreign Key → machines.machine_id)
   - Defines which machines are eligible for each operation

### Planning Models

6. **MonthlyPlan** (`monthly_plans` table)
   - `plan_id` (Primary Key)
   - `part_id` (Foreign Key → parts.part_id)
   - `company_id` (Foreign Key → companies.company_id)
   - `month` (Date)
   - `planned_quantity`

7. **ForecastPlan** (`forecast_plans` table)
   - `forecast_id` (Primary Key)
   - `part_id` (Foreign Key → parts.part_id)
   - `company_id` (Foreign Key → companies.company_id)
   - `month` (Date)
   - `week` (1-4)
   - `forecasted_quantity`

8. **ProductionSchedule** (`production_schedules` table)
   - `schedule_id` (Primary Key)
   - `date` (Date)
   - `shift_number` (1-2, 2 shifts per day)
   - `slot_number` (1-2, 2 slots per shift = 4 slots per day)
   - `part_id` (Foreign Key → parts.part_id)
   - `operation_id` (Foreign Key → operations.operation_id)
   - `machine_id` (Foreign Key → machines.machine_id)
   - `quantity_scheduled`
   - `sub_batch_id` (for tracking sub-batches)
   - `status` (planned, in_progress, completed, delayed)

## API Endpoints

### Companies
- `GET /companies` - List all companies
- `POST /companies` - Create a new company
- `GET /companies/<id>` - Get company by ID
- `PUT /companies/<id>` - Update company
- `DELETE /companies/<id>` - Delete company

### Parts
- `GET /parts` - List all parts
- `POST /parts` - Create a new part
- `GET /parts/<id>` - Get part by ID
- `PUT /parts/<id>` - Update part
- `DELETE /parts/<id>` - Delete part
- `GET /parts/<id>/operations` - Get operations for a specific part

### Operations
- `GET /operations` - List all operations
- `POST /operations` - Create a new operation
- `GET /operations/<id>` - Get operation by ID
- `PUT /operations/<id>` - Update operation
- `DELETE /operations/<id>` - Delete operation
- `GET /operations/<operation_id>/eligible-machines` - Get eligible machines for an operation
- `POST /operations/<operation_id>/machines/<machine_id>` - Add machine as eligible for operation
- `DELETE /operations/<operation_id>/machines/<machine_id>` - Remove machine from operation

### Machines
- `GET /machines` - List all machines
- `POST /machines` - Create a new machine

### Production Schedules
- `GET /production-schedules` - List all production schedules (supports filtering by date, machine_id, part_id)
- `POST /production-schedules` - Create a new production schedule
- `GET /production-schedules/<id>` - Get production schedule by ID
- `PUT /production-schedules/<id>` - Update production schedule
- `DELETE /production-schedules/<id>` - Delete production schedule
- `PUT /production-schedules/<id>/status` - Update only the status of a production schedule (for sub-batch tracking)
- `GET /production-schedules/by-date/<date>` - Get schedules for a specific date
- `GET /production-schedules/by-machine/<machine_id>` - Get schedules for a specific machine (supports optional date filtering)
- `GET /production-schedules/by-part/<part_id>` - Get schedules for a specific part

### Monthly Plans
- `GET /monthly-plans` - List all monthly plans
- `POST /monthly-plans` - Create a new monthly plan (supersedes existing plan for same company/part/month)
- `GET /monthly-plans/<id>` - Get monthly plan by ID
- `PUT /monthly-plans/<id>` - Update monthly plan
- `DELETE /monthly-plans/<id>` - Delete monthly plan

### Forecast Plans
- `GET /forecast-plans` - List all forecast plans
- `POST /forecast-plans` - Create a new forecast plan (supersedes existing forecast for same company/part/month/week)
- `GET /forecast-plans/<id>` - Get forecast plan by ID
- `PUT /forecast-plans/<id>` - Update forecast plan
- `DELETE /forecast-plans/<id>` - Delete forecast plan

### Testing
- `GET /test-db` - Test database connectivity and show table counts

## Key Features

### Relationships
- Companies have multiple Parts
- Parts have multiple Operations (ordered by sequence_number)
- Operations can run on multiple Machines (many-to-many)
- Machines can handle multiple Operations

### Querying Eligible Machines
```python
operation = Operation.query.get(operation_id)
eligible_machines = operation.get_eligible_machines()
```

### Production Scheduling
- 2 shifts per day, 2 slots per shift = 4 total slots per day
- Supports sub-batch tracking with unique sub_batch_id
- Status tracking for operations: planned, in_progress, completed, delayed
- Machine assignment and progress tracking per slot
- Filtering capabilities by date, machine, and part
- Conflict detection for double-booked slots

### Monthly Plans & Forecasts
- **Supersede Logic**: New schedules automatically replace previous schedules for the same company/part/month
- **Forecast Support**: Supports 1-2 months of forecast data with weekly granularity (weeks 1-4)
- **Data Separation**: Monthly plans and forecast plans are stored in separate tables
- **Date Format**: All dates should be provided in ISO format (YYYY-MM-DD)

## Testing

Run the test script to validate all models:

```bash
python test_models.py
```

This will create sample data and test all CRUD operations, relationships, and key functionality.

Run the schedule API tests:

```bash
python test_schedule_api.py
```

This will test all schedule-related endpoints including supersede logic and error handling.

Run the production schedule API tests:

```bash
python test_production_schedule_api.py
```

This will test all production schedule endpoints including sub-batch tracking, status updates, and filtering capabilities.

Run the schedule API tests:

```bash
python test_schedule_api.py
```

This will test all schedule-related endpoints including supersede logic and error handling.

## Database

The application uses SQLite by default. The database file (`scheduling.db`) is created automatically when the application starts.

For production, you can change the database URL in `app/__init__.py`.