from app import db
from datetime import datetime

class ForecastPlan(db.Model):
    __tablename__ = 'forecast_plans'
    
    forecast_id = db.Column(db.Integer, primary_key=True)
    part_id = db.Column(db.Integer, db.ForeignKey('parts.part_id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.company_id'), nullable=False)
    month = db.Column(db.Date, nullable=False)  # Month/Year for the forecast
    week = db.Column(db.Integer, nullable=False)  # Week number within the month (1-4)
    forecasted_quantity = db.Column(db.Integer, nullable=False)
    
    # Add index for faster queries
    __table_args__ = (
        db.Index('idx_forecast_plan_part_company_month_week', 'part_id', 'company_id', 'month', 'week'),
    )
    
    def __repr__(self):
        return f'<ForecastPlan {self.forecast_id} - Part:{self.part_id} - Week:{self.week} - Qty:{self.forecasted_quantity}>'
    
    def to_dict(self):
        return {
            'forecast_id': self.forecast_id,
            'part_id': self.part_id,
            'company_id': self.company_id,
            'month': self.month.isoformat() if self.month else None,
            'week': self.week,
            'forecasted_quantity': self.forecasted_quantity
        }