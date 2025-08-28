from app import db

# Association table for many-to-many relationship between Operations and Machines
class OperationMachine(db.Model):
    __tablename__ = 'operation_machines'
    
    operation_id = db.Column(db.Integer, db.ForeignKey('operations.operation_id'), primary_key=True)
    machine_id = db.Column(db.Integer, db.ForeignKey('machines.machine_id'), primary_key=True)
    
    def __repr__(self):
        return f'<OperationMachine Operation:{self.operation_id} - Machine:{self.machine_id}>'
    
    def to_dict(self):
        return {
            'operation_id': self.operation_id,
            'machine_id': self.machine_id
        }