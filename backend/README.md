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
- Supports sub-batch tracking
- Status tracking for operations
- Conflict detection for double-booked slots

## Testing

Run the test script to validate all models:

```bash
python test_models.py
```

This will create sample data and test all CRUD operations, relationships, and key functionality.

## Database

The application uses SQLite by default. The database file (`scheduling.db`) is created automatically when the application starts.

For production, you can change the database URL in `app/__init__.py`.