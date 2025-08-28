from app import db
from datetime import datetime

class MonthlyPlan(db.Model):
    __tablename__ = 'monthly_plans'
    
    plan_id = db.Column(db.Integer, primary_key=True)
    part_id = db.Column(db.Integer, db.ForeignKey('parts.part_id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.company_id'), nullable=False)
    month = db.Column(db.Date, nullable=False)  # Month/Year for the plan
    planned_quantity = db.Column(db.Integer, nullable=False)
    
    # Add index for faster queries
    __table_args__ = (
        db.Index('idx_monthly_plan_part_company_month', 'part_id', 'company_id', 'month'),
    )
    
    def __repr__(self):
        return f'<MonthlyPlan {self.plan_id} - Part:{self.part_id} - Qty:{self.planned_quantity}>'
    
    def to_dict(self):
        return {
            'plan_id': self.plan_id,
            'part_id': self.part_id,
            'company_id': self.company_id,
            'month': self.month.isoformat() if self.month else None,
            'planned_quantity': self.planned_quantity
        }