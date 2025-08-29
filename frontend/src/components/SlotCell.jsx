import { useState, useEffect } from 'react';

const SlotCell = ({ 
  part, 
  date, 
  shift, 
  slot, 
  machines, 
  operations, 
  schedule,
  conflictInfo,
  onScheduleUpdate,
  onScheduleCreate,
  onScheduleDelete 
}) => {
  const [selectedMachine, setSelectedMachine] = useState(schedule?.machine_id || '');
  const [selectedOperation, setSelectedOperation] = useState(schedule?.operation_id || '');
  const [quantity, setQuantity] = useState(schedule?.quantity_scheduled || '');
  const [subBatchId, setSubBatchId] = useState(schedule?.sub_batch_id || '');
  const [isSelected, setIsSelected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Use conflictInfo to determine if slot has conflicts
  const hasConflict = conflictInfo?.hasConflicts || false;

  // Filter operations for this specific part
  const partOperations = operations.filter(op => op.part_id === part.part_id);

  const handleMachineChange = async (e) => {
    const machineId = e.target.value;
    setSelectedMachine(machineId);
    
    if (machineId && selectedOperation && quantity) {
      await handleScheduleChange(machineId, selectedOperation, quantity, subBatchId);
    }
  };

  const handleOperationChange = async (e) => {
    const operationId = e.target.value;
    setSelectedOperation(operationId);
    
    if (selectedMachine && operationId && quantity) {
      await handleScheduleChange(selectedMachine, operationId, quantity, subBatchId);
    }
  };

  const handleQuantityChange = async (e) => {
    const newQuantity = e.target.value;
    setQuantity(newQuantity);
    
    if (selectedMachine && selectedOperation && newQuantity) {
      await handleScheduleChange(selectedMachine, selectedOperation, newQuantity, subBatchId);
    }
  };

  const handleSubBatchChange = async (e) => {
    const newSubBatchId = e.target.value;
    setSubBatchId(newSubBatchId);
    
    if (selectedMachine && selectedOperation && quantity) {
      await handleScheduleChange(selectedMachine, selectedOperation, quantity, newSubBatchId);
    }
  };

  const handleScheduleChange = async (machineId, operationId, scheduleQuantity, batchId) => {
    if (!machineId || !operationId || !scheduleQuantity) return;

    setIsLoading(true);
    try {
      const scheduleData = {
        date: date,
        shift_number: shift,
        slot_number: slot,
        part_id: part.part_id,
        operation_id: parseInt(operationId),
        machine_id: parseInt(machineId),
        quantity_scheduled: parseInt(scheduleQuantity),
        sub_batch_id: batchId || null,
        status: 'planned'
      };

      if (schedule) {
        // Update existing schedule
        await onScheduleUpdate(schedule.schedule_id, scheduleData);
      } else {
        // Create new schedule
        await onScheduleCreate(scheduleData);
      }

      // Check for conflicts after scheduling
      // This will be handled by the parent component
      
    } catch (error) {
      console.error('Error updating schedule:', error);
      // Handle error (could show toast notification)
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearSlot = async () => {
    if (schedule) {
      setIsLoading(true);
      try {
        await onScheduleDelete(schedule.schedule_id);
        setSelectedMachine('');
        setSelectedOperation('');
        setQuantity('');
        setSubBatchId('');
        setIsSelected(false);
      } catch (error) {
        console.error('Error clearing slot:', error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const getSlotStyle = () => {
    let baseStyle = "border rounded p-1 m-0.5 text-xs min-h-[80px] relative";
    
    if (hasConflict) {
      baseStyle += " border-red-500 bg-red-100";
    } else if (selectedMachine) {
      baseStyle += " border-green-500 bg-green-50";
    } else {
      baseStyle += " border-gray-300 bg-white hover:bg-gray-50";
    }

    if (isSelected) {
      baseStyle += " ring-2 ring-blue-500";
    }

    if (isLoading) {
      baseStyle += " opacity-50";
    }

    return baseStyle;
  };

  // Generate conflict tooltip content
  const getConflictTooltipContent = () => {
    if (!hasConflict || !conflictInfo?.conflicts) return '';
    
    const conflictLines = [];
    conflictInfo.conflicts.forEach((conflict, index) => {
      const machine = machines.find(m => m.machine_id === conflict.machineId);
      conflictLines.push(`Machine: ${machine?.name || conflict.machineId}`);
      
      conflict.schedules.forEach((schedule, schedIndex) => {
        const operation = operations.find(op => op.operation_id === schedule.operation_id);
        const conflictPart = schedule.part_id === part.part_id ? part : { name: `Part ${schedule.part_id}` };
        conflictLines.push(`  Schedule ${schedIndex + 1}: ${conflictPart.name} - Operation ${operation?.sequence_number || schedule.operation_id} (${schedule.quantity_scheduled} qty)`);
      });
    });
    
    return `Scheduling Conflict:\n${conflictLines.join('\n')}`;
  };

  const selectedMachineData = machines.find(m => m.machine_id === parseInt(selectedMachine));
  const selectedOperationData = partOperations.find(op => op.operation_id === parseInt(selectedOperation));

  return (
    <div className={getSlotStyle()}>
      {/* Slot identifier */}
      <div className="text-gray-500 text-[10px] absolute top-0 left-1">
        S{shift}:{slot}
      </div>

      {/* Machine dropdown */}
      <select
        value={selectedMachine}
        onChange={handleMachineChange}
        className="w-full text-[10px] border-0 bg-transparent focus:ring-1 focus:ring-blue-500 rounded mb-1"
        disabled={isLoading}
      >
        <option value="">Select Machine</option>
        {machines.map(machine => (
          <option key={machine.machine_id} value={machine.machine_id}>
            {machine.name}
          </option>
        ))}
      </select>

      {/* Operation dropdown */}
      {selectedMachine && (
        <select
          value={selectedOperation}
          onChange={handleOperationChange}
          className="w-full text-[10px] border-0 bg-transparent focus:ring-1 focus:ring-blue-500 rounded mb-1"
          disabled={isLoading}
        >
          <option value="">Select Operation</option>
          {partOperations.map(operation => (
            <option key={operation.operation_id} value={operation.operation_id}>
              OP{operation.sequence_number} ({operation.machining_time}min)
            </option>
          ))}
        </select>
      )}

      {/* Quantity input */}
      {selectedMachine && selectedOperation && (
        <input
          type="number"
          placeholder="Qty"
          value={quantity}
          onChange={handleQuantityChange}
          className="w-full text-[10px] border-0 bg-transparent focus:ring-1 focus:ring-blue-500 rounded mb-1"
          disabled={isLoading}
          min="1"
        />
      )}

      {/* Sub-batch input */}
      {selectedMachine && selectedOperation && quantity && (
        <input
          type="text"
          placeholder="Sub-batch ID"
          value={subBatchId}
          onChange={handleSubBatchChange}
          className="w-full text-[10px] border-0 bg-transparent focus:ring-1 focus:ring-blue-500 rounded mb-1"
          disabled={isLoading}
        />
      )}

      {/* Selection checkbox */}
      <div className="absolute bottom-1 left-1">
        <input
          type="checkbox"
          checked={isSelected}
          onChange={(e) => setIsSelected(e.target.checked)}
          className="w-3 h-3"
          disabled={isLoading}
        />
      </div>

      {/* Clear button */}
      {schedule && (
        <button
          onClick={handleClearSlot}
          className="absolute bottom-1 right-1 text-red-500 text-[10px] hover:text-red-700"
          disabled={isLoading}
          title="Clear slot"
        >
          ✕
        </button>
      )}

      {/* Conflict indicator */}
      {hasConflict && (
        <div 
          className="absolute top-0 right-1 text-red-500 text-xs cursor-help" 
          title={getConflictTooltipContent()}
        >
          ⚠️
        </div>
      )}

      {/* Loading indicator */}
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-50">
          <div className="text-xs">...</div>
        </div>
      )}
    </div>
  );
};

export default SlotCell;