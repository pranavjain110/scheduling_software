import SlotCell from './SlotCell';

const DayColumn = ({ 
  date, 
  part, 
  machines, 
  operations, 
  schedules,
  onScheduleUpdate,
  onScheduleCreate,
  onScheduleDelete 
}) => {
  // Format date for display
  const dateObj = new Date(date);
  const dayName = dateObj.toLocaleDateString('en-US', { weekday: 'short' });
  const dateStr = dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });

  // Filter schedules for this specific part and date
  const daySchedules = schedules.filter(s => 
    s.date === date && s.part_id === part.part_id
  );

  // Get schedule for a specific slot
  const getScheduleForSlot = (shift, slot) => {
    return daySchedules.find(s => 
      s.shift_number === shift && s.slot_number === slot
    );
  };

  // Check if it's a weekend
  const isWeekend = dateObj.getDay() === 0 || dateObj.getDay() === 6;

  return (
    <div className={`min-w-[120px] ${isWeekend ? 'bg-gray-100' : ''}`}>
      {/* Day header */}
      <div className="text-center p-2 border-b border-gray-300 bg-gray-50 sticky top-0 z-10">
        <div className="font-semibold text-sm text-gray-800">{dayName}</div>
        <div className="text-xs text-gray-600">{dateStr}</div>
      </div>

      {/* 4 slots arranged in 2x2 grid */}
      <div className="p-1">
        {/* Shift 1 */}
        <div className="mb-1">
          <div className="text-xs text-gray-600 text-center mb-1 font-medium">Shift 1</div>
          <div className="grid grid-cols-2 gap-1">
            <SlotCell
              part={part}
              date={date}
              shift={1}
              slot={1}
              machines={machines}
              operations={operations}
              schedule={getScheduleForSlot(1, 1)}
              onScheduleUpdate={onScheduleUpdate}
              onScheduleCreate={onScheduleCreate}
              onScheduleDelete={onScheduleDelete}
            />
            <SlotCell
              part={part}
              date={date}
              shift={1}
              slot={2}
              machines={machines}
              operations={operations}
              schedule={getScheduleForSlot(1, 2)}
              onScheduleUpdate={onScheduleUpdate}
              onScheduleCreate={onScheduleCreate}
              onScheduleDelete={onScheduleDelete}
            />
          </div>
        </div>

        {/* Shift 2 */}
        <div>
          <div className="text-xs text-gray-600 text-center mb-1 font-medium">Shift 2</div>
          <div className="grid grid-cols-2 gap-1">
            <SlotCell
              part={part}
              date={date}
              shift={2}
              slot={1}
              machines={machines}
              operations={operations}
              schedule={getScheduleForSlot(2, 1)}
              onScheduleUpdate={onScheduleUpdate}
              onScheduleCreate={onScheduleCreate}
              onScheduleDelete={onScheduleDelete}
            />
            <SlotCell
              part={part}
              date={date}
              shift={2}
              slot={2}
              machines={machines}
              operations={operations}
              schedule={getScheduleForSlot(2, 2)}
              onScheduleUpdate={onScheduleUpdate}
              onScheduleCreate={onScheduleCreate}
              onScheduleDelete={onScheduleDelete}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default DayColumn;