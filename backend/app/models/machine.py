from app import db

class Machine(db.Model):
    __tablename__ = 'machines'
    
    machine_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    
    # Relationships
    production_schedules = db.relationship('ProductionSchedule', backref='machine', lazy=True)
    
    def __repr__(self):
        return f'<Machine {self.name}>'
    
    def to_dict(self):
        return {
            'machine_id': self.machine_id,
            'name': self.name,
            'type': self.type
        }