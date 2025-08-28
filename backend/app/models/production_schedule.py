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