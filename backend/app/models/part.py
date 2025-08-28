from app import db

class Part(db.Model):
    __tablename__ = 'parts'
    
    part_id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.company_id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    total_operations = db.Column(db.Integer, nullable=False, default=0)
    
    # Relationships
    operations = db.relationship('Operation', backref='part', lazy=True, cascade='all, delete-orphan')
    monthly_plans = db.relationship('MonthlyPlan', backref='part', lazy=True, cascade='all, delete-orphan')
    forecast_plans = db.relationship('ForecastPlan', backref='part', lazy=True, cascade='all, delete-orphan')
    production_schedules = db.relationship('ProductionSchedule', backref='part', lazy=True)
    
    def __repr__(self):
        return f'<Part {self.name}>'
    
    def to_dict(self):
        return {
            'part_id': self.part_id,
            'company_id': self.company_id,
            'name': self.name,
            'total_operations': self.total_operations
        }