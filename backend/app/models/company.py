from app import db

class Company(db.Model):
    __tablename__ = 'companies'
    
    company_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    
    # Relationships
    parts = db.relationship('Part', backref='company', lazy=True, cascade='all, delete-orphan')
    monthly_plans = db.relationship('MonthlyPlan', backref='company', lazy=True, cascade='all, delete-orphan')
    forecast_plans = db.relationship('ForecastPlan', backref='company', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Company {self.name}>'
    
    def to_dict(self):
        return {
            'company_id': self.company_id,
            'name': self.name
        }