import { useMemo } from 'react';

const GanttChart = ({ 
  machines, 
  schedules, 
  selectedDateRange, 
  parts, 
  operations 
}) => {
  // Generate date range for timeline
  const generateDateRange = (startDate, endDate) => {
    const dates = [];
    const current = new Date(startDate);
    const end = new Date(endDate);
    
    while (current <= end) {
      dates.push(current.toISOString().split('T')[0]);
      current.setDate(current.getDate() + 1);
    }
    return dates;
  };

  const dateRange = generateDateRange(selectedDateRange.start, selectedDateRange.end);

  // Get status color for schedule
  const getStatusColor = (status) => {
    switch (status) {
      case 'planned':
        return 'bg-blue-200 border-blue-400 text-blue-800';
      case 'in_progress':
        return 'bg-yellow-200 border-yellow-400 text-yellow-800';
      case 'completed':
        return 'bg-green-200 border-green-400 text-green-800';
      case 'delayed':
        return 'bg-red-200 border-red-400 text-red-800';
      default:
        return 'bg-gray-200 border-gray-400 text-gray-800';
    }
  };

  // Group schedules by machine and detect conflicts
  const machineSchedules = useMemo(() => {
    const grouped = {};
    
    machines.forEach(machine => {
      grouped[machine.machine_id] = {
        machine,
        schedules: schedules.filter(s => s.machine_id === machine.machine_id),
        conflicts: []
      };
    });

    // Detect conflicts (multiple schedules in same slot)
    Object.values(grouped).forEach(machineGroup => {
      const slotMap = {};
      
      machineGroup.schedules.forEach(schedule => {
        const slotKey = `${schedule.date}_${schedule.shift_number}_${schedule.slot_number}`;
        if (!slotMap[slotKey]) {
          slotMap[slotKey] = [];
        }
        slotMap[slotKey].push(schedule);
      });
      
      // Find slots with multiple schedules (conflicts)
      Object.entries(slotMap).forEach(([slotKey, slotSchedules]) => {
        if (slotSchedules.length > 1) {
          machineGroup.conflicts.push({
            slotKey,
            schedules: slotSchedules,
            date: slotSchedules[0].date,
            shift: slotSchedules[0].shift_number,
            slot: slotSchedules[0].slot_number
          });
        }
      });
    });

    return grouped;
  }, [machines, schedules]);

  // Get part name by ID
  const getPartName = (partId) => {
    const part = parts.find(p => p.part_id === partId);
    return part ? part.name : `Part ${partId}`;
  };

  // Get operation sequence by ID
  const getOperationSequence = (operationId) => {
    const operation = operations.find(op => op.operation_id === operationId);
    return operation ? `OP${operation.sequence_number}` : `OP${operationId}`;
  };

  // Get schedule position and width based on shift/slot
  const getSchedulePosition = (schedule, dateIndex) => {
    const dayWidth = 120; // Width per day column
    const slotWidth = dayWidth / 4; // 4 slots per day (2 shifts × 2 slots)
    const slotIndex = (schedule.shift_number - 1) * 2 + (schedule.slot_number - 1);
    
    return {
      left: dateIndex * dayWidth + slotIndex * slotWidth,
      width: slotWidth - 2 // Small gap between slots
    };
  };

  // Check if a schedule is part of a conflict
  const isConflicted = (schedule, machineGroup) => {
    return machineGroup.conflicts.some(conflict => 
      conflict.schedules.some(s => s.schedule_id === schedule.schedule_id)
    );
  };

  if (!machines.length) {
    return (
      <div className="p-8 text-center text-gray-500">
        <div className="text-xl font-semibold mb-2">No Machines Available</div>
        <div>Add machines to see the Gantt chart visualization</div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Gantt Header */}
      <div className="bg-white border-b border-gray-300 p-4">
        <h2 className="text-xl font-bold text-gray-800 mb-2">Machine Schedule - Gantt View</h2>
        <div className="flex gap-6 text-sm">
          {/* Status Legend */}
          <div className="flex items-center gap-4">
            <span className="font-medium text-gray-700">Status:</span>
            <div className="flex gap-2">
              <span className={`px-2 py-1 rounded text-xs border ${getStatusColor('planned')}`}>
                Planned
              </span>
              <span className={`px-2 py-1 rounded text-xs border ${getStatusColor('in_progress')}`}>
                In Progress
              </span>
              <span className={`px-2 py-1 rounded text-xs border ${getStatusColor('completed')}`}>
                Completed
              </span>
              <span className={`px-2 py-1 rounded text-xs border ${getStatusColor('delayed')}`}>
                Delayed
              </span>
            </div>
          </div>
          <div className="text-gray-600">
            <span className="px-2 py-1 bg-red-100 border border-red-300 text-red-800 text-xs rounded">
              ⚠️ Conflict
            </span>
          </div>
        </div>
      </div>

      {/* Gantt Chart */}
      <div className="flex-1 overflow-auto">
        <div className="min-w-full">
          {/* Date Headers */}
          <div className="sticky top-0 z-10 bg-gray-50 border-b border-gray-300 flex">
            {/* Machine column header */}
            <div className="min-w-[200px] p-3 border-r border-gray-300 bg-gray-100 font-semibold text-gray-800">
              Machine
            </div>
            
            {/* Date column headers */}
            {dateRange.map(date => {
              const dateObj = new Date(date);
              const dayName = dateObj.toLocaleDateString('en-US', { weekday: 'short' });
              const dateStr = dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
              const isWeekend = dateObj.getDay() === 0 || dateObj.getDay() === 6;
              
              return (
                <div 
                  key={date} 
                  className={`min-w-[120px] p-2 text-center border-r border-gray-300 ${isWeekend ? 'bg-gray-200' : 'bg-gray-50'}`}
                >
                  <div className="font-semibold text-gray-800">{dayName}</div>
                  <div className="text-xs text-gray-600">{dateStr}</div>
                  <div className="text-xs text-gray-500 mt-1">
                    S1:1-2 | S2:1-2
                  </div>
                </div>
              );
            })}
          </div>

          {/* Machine Rows */}
          {Object.values(machineSchedules).map(machineGroup => (
            <div key={machineGroup.machine.machine_id} className="border-b border-gray-200 flex">
              {/* Machine info column */}
              <div className="min-w-[200px] p-4 border-r border-gray-300 bg-gray-50">
                <div className="font-medium text-gray-800">{machineGroup.machine.name}</div>
                <div className="text-xs text-gray-600">Type: {machineGroup.machine.type}</div>
                <div className="text-xs text-gray-600">ID: {machineGroup.machine.machine_id}</div>
                {machineGroup.conflicts.length > 0 && (
                  <div className="text-xs text-red-600 mt-1">
                    ⚠️ {machineGroup.conflicts.length} conflict(s)
                  </div>
                )}
              </div>
              
              {/* Timeline */}
              <div className="flex-1 relative">
                <div className="flex">
                  {dateRange.map((date) => {
                    const isWeekend = new Date(date).getDay() === 0 || new Date(date).getDay() === 6;
                    
                    return (
                      <div 
                        key={date} 
                        className={`min-w-[120px] min-h-[80px] border-r border-gray-300 relative ${isWeekend ? 'bg-gray-100' : 'bg-white'}`}
                      >
                        {/* Slot grid lines */}
                        <div className="absolute inset-0 flex">
                          {[0, 1, 2, 3].map(slotIndex => (
                            <div key={slotIndex} className="flex-1 border-r border-gray-200 border-dashed"></div>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
                
                {/* Schedule blocks */}
                <div className="absolute inset-0">
                  {machineGroup.schedules
                    .filter(schedule => dateRange.includes(schedule.date))
                    .map(schedule => {
                      const dateIndex = dateRange.indexOf(schedule.date);
                      const position = getSchedulePosition(schedule, dateIndex);
                      const isConflict = isConflicted(schedule, machineGroup);
                      
                      return (
                        <div
                          key={schedule.schedule_id}
                          className={`absolute top-1 border rounded text-xs p-1 cursor-pointer transition-all hover:z-20 hover:scale-105 ${
                            getStatusColor(schedule.status)
                          } ${isConflict ? 'ring-2 ring-red-500 ring-opacity-75' : ''}`}
                          style={{
                            left: `${position.left}px`,
                            width: `${position.width}px`,
                            height: '60px'
                          }}
                          title={`${getPartName(schedule.part_id)} - ${getOperationSequence(schedule.operation_id)}
Date: ${schedule.date}
Shift: ${schedule.shift_number}, Slot: ${schedule.slot_number}
Status: ${schedule.status}
Quantity: ${schedule.quantity_scheduled}
Sub-batch: ${schedule.sub_batch_id || 'None'}${isConflict ? '\n⚠️ CONFLICT DETECTED' : ''}`}
                        >
                          <div className="font-semibold truncate">
                            {getPartName(schedule.part_id)}
                          </div>
                          <div className="text-xs truncate">
                            {getOperationSequence(schedule.operation_id)}
                          </div>
                          <div className="text-xs truncate">
                            Qty: {schedule.quantity_scheduled}
                          </div>
                          {isConflict && (
                            <div className="text-xs text-red-700 font-bold">
                              ⚠️ CONFLICT
                            </div>
                          )}
                        </div>
                      );
                    })}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default GanttChart;