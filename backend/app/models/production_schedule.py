from app import db
from datetime import datetime

class ProductionSchedule(db.Model):
    __tablename__ = 'production_schedules'
    
    schedule_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    shift_number = db.Column(db.Integer, nullable=False)  # 1 or 2 (2 shifts per day)
    slot_number = db.Column(db.Integer, nullable=False)   # 1 or 2 (2 slots per shift, 4 total per day)
    part_id = db.Column(db.Integer, db.ForeignKey('parts.part_id'), nullable=False)
    operation_id = db.Column(db.Integer, db.ForeignKey('operations.operation_id'), nullable=False)
    machine_id = db.Column(db.Integer, db.ForeignKey('machines.machine_id'), nullable=False)
    quantity_scheduled = db.Column(db.Integer, nullable=False)
    sub_batch_id = db.Column(db.String(50), nullable=True)  # For tracking sub-batches
    status = db.Column(db.String(50), nullable=False, default='planned')  # planned, in_progress, completed, delayed
    
    # Add constraints and indexes
    __table_args__ = (
        db.Index('idx_schedule_date_shift_slot', 'date', 'shift_number', 'slot_number'),
        db.Index('idx_schedule_part_operation', 'part_id', 'operation_id'),
        db.Index('idx_schedule_machine_date', 'machine_id', 'date'),
    )
    
    def __repr__(self):
        return f'<ProductionSchedule {self.schedule_id} - {self.date} S{self.shift_number}:{self.slot_number} - Machine:{self.machine_id}>'
    
    def to_dict(self):
        return {
            'schedule_id': self.schedule_id,
            'date': self.date.isoformat() if self.date else None,
            'shift_number': self.shift_number,
            'slot_number': self.slot_number,
            'part_id': self.part_id,
            'operation_id': self.operation_id,
            'machine_id': self.machine_id,
            'quantity_scheduled': self.quantity_scheduled,
            'sub_batch_id': self.sub_batch_id,
            'status': self.status
        }
    
    @classmethod
    def get_machine_schedule(cls, machine_id, date):
        """Get all schedules for a specific machine on a specific date"""
        return cls.query.filter_by(machine_id=machine_id, date=date).all()
    
    @classmethod
    def check_slot_availability(cls, machine_id, date, shift_number, slot_number):
        """Check if a specific slot is available for a machine"""
        existing = cls.query.filter_by(
            machine_id=machine_id,
            date=date,
            shift_number=shift_number,
            slot_number=slot_number
        ).first()
        return existing is None
    
    @classmethod
    def get_slot_conflicts(cls, machine_id, date, shift_number, slot_number, exclude_schedule_id=None):
        """Get detailed information about conflicts for a specific slot"""
        query = cls.query.filter_by(
            machine_id=machine_id,
            date=date,
            shift_number=shift_number,
            slot_number=slot_number
        )
        
        # Exclude a specific schedule ID when checking for conflicts (useful for updates)
        if exclude_schedule_id:
            query = query.filter(cls.schedule_id != exclude_schedule_id)
        
        conflicting_schedules = query.all()
        
        if not conflicting_schedules:
            return None
        
        # Return detailed conflict information
        conflicts = []
        for schedule in conflicting_schedules:
            conflicts.append({
                'schedule_id': schedule.schedule_id,
                'part_id': schedule.part_id,
                'operation_id': schedule.operation_id,
                'quantity_scheduled': schedule.quantity_scheduled,
                'sub_batch_id': schedule.sub_batch_id,
                'status': schedule.status,
                'slot_info': {
                    'machine_id': machine_id,
                    'date': date.isoformat() if hasattr(date, 'isoformat') else str(date),
                    'shift_number': shift_number,
                    'slot_number': slot_number
                }
            })
        
        return conflicts
    
    @classmethod
    def get_machine_conflicts(cls, machine_id, date=None):
        """Get all conflicts for a specific machine on a specific date or all dates"""
        query = cls.query.filter_by(machine_id=machine_id)
        
        if date:
            query = query.filter_by(date=date)
        
        schedules = query.all()
        
        # Group schedules by (date, shift_number, slot_number) to find conflicts
        slot_groups = {}
        for schedule in schedules:
            key = (schedule.date, schedule.shift_number, schedule.slot_number)
            if key not in slot_groups:
                slot_groups[key] = []
            slot_groups[key].append(schedule)
        
        # Find slots with more than one schedule (conflicts)
        conflicts = []
        for (date, shift_number, slot_number), slot_schedules in slot_groups.items():
            if len(slot_schedules) > 1:
                conflict_info = {
                    'slot_info': {
                        'machine_id': machine_id,
                        'date': date.isoformat() if hasattr(date, 'isoformat') else str(date),
                        'shift_number': shift_number,
                        'slot_number': slot_number
                    },
                    'conflicting_schedules': []
                }
                
                for schedule in slot_schedules:
                    conflict_info['conflicting_schedules'].append({
                        'schedule_id': schedule.schedule_id,
                        'part_id': schedule.part_id,
                        'operation_id': schedule.operation_id,
                        'quantity_scheduled': schedule.quantity_scheduled,
                        'sub_batch_id': schedule.sub_batch_id,
                        'status': schedule.status
                    })
                
                conflicts.append(conflict_info)
        
        return conflicts
    
    @classmethod
    def get_date_conflicts(cls, date):
        """Get all conflicts for a specific date across all machines"""
        schedules = cls.query.filter_by(date=date).all()
        
        # Group schedules by (machine_id, shift_number, slot_number) to find conflicts
        slot_groups = {}
        for schedule in schedules:
            key = (schedule.machine_id, schedule.shift_number, schedule.slot_number)
            if key not in slot_groups:
                slot_groups[key] = []
            slot_groups[key].append(schedule)
        
        # Find slots with more than one schedule (conflicts)
        conflicts = []
        for (machine_id, shift_number, slot_number), slot_schedules in slot_groups.items():
            if len(slot_schedules) > 1:
                conflict_info = {
                    'slot_info': {
                        'machine_id': machine_id,
                        'date': date.isoformat() if hasattr(date, 'isoformat') else str(date),
                        'shift_number': shift_number,
                        'slot_number': slot_number
                    },
                    'conflicting_schedules': []
                }
                
                for schedule in slot_schedules:
                    conflict_info['conflicting_schedules'].append({
                        'schedule_id': schedule.schedule_id,
                        'part_id': schedule.part_id,
                        'operation_id': schedule.operation_id,
                        'quantity_scheduled': schedule.quantity_scheduled,
                        'sub_batch_id': schedule.sub_batch_id,
                        'status': schedule.status
                    })
                
                conflicts.append(conflict_info)
        
        return conflicts