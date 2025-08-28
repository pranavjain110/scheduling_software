from app import db

class Operation(db.Model):
    __tablename__ = 'operations'
    
    operation_id = db.Column(db.Integer, primary_key=True)
    part_id = db.Column(db.Integer, db.ForeignKey('parts.part_id'), nullable=False)
    sequence_number = db.Column(db.Integer, nullable=False)
    machining_time = db.Column(db.Float, nullable=False)  # Time in minutes
    loading_time = db.Column(db.Float, nullable=False)    # Time in minutes
    
    # Relationships
    production_schedules = db.relationship('ProductionSchedule', backref='operation', lazy=True)
    # Many-to-many relationship with machines through OperationMachine
    eligible_machines = db.relationship('Machine', secondary='operation_machines', 
                                      backref=db.backref('eligible_operations', lazy='dynamic'),
                                      lazy='dynamic')
    
    def __repr__(self):
        return f'<Operation {self.operation_id} - Part {self.part_id} - Seq {self.sequence_number}>'
    
    def to_dict(self):
        return {
            'operation_id': self.operation_id,
            'part_id': self.part_id,
            'sequence_number': self.sequence_number,
            'machining_time': self.machining_time,
            'loading_time': self.loading_time
        }
    
    def get_eligible_machines(self):
        """Return list of machines eligible for this operation"""
        return self.eligible_machines.all()