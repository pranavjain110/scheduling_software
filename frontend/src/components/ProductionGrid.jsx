import DayColumn from './DayColumn';

const ProductionGrid = ({ 
  parts, 
  machines, 
  operations, 
  schedules, 
  selectedDateRange,
  onScheduleCreate,
  onScheduleUpdate,
  onScheduleDelete
}) => {
  // Generate date range for columns
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

  return (
    <div className="h-full flex flex-col">
      {/* Grid */}
      <div className="flex-1 overflow-auto">
        <div className="min-w-full">
          {/* Grid header with dates */}
          <div className="sticky top-0 z-20 bg-white border-b border-gray-300 flex">
            {/* Parts column header */}
            <div className="min-w-[200px] p-4 border-r border-gray-300 bg-gray-50 font-semibold text-gray-800">
              Parts
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
                </div>
              );
            })}
          </div>

          {/* Grid rows */}
          {parts.map(part => (
            <div key={part.part_id} className="border-b border-gray-200 flex">
              {/* Part name column */}
              <div className="min-w-[200px] p-4 border-r border-gray-300 bg-gray-50">
                <div className="font-medium text-gray-800">{part.name}</div>
                <div className="text-xs text-gray-600">ID: {part.part_id}</div>
                <div className="text-xs text-gray-600">Operations: {part.total_operations}</div>
              </div>
              
              {/* Day columns */}
              {dateRange.map(date => (
                <DayColumn
                  key={`${part.part_id}-${date}`}
                  date={date}
                  part={part}
                  machines={machines}
                  operations={operations}
                  schedules={schedules}
                  onScheduleUpdate={onScheduleUpdate}
                  onScheduleCreate={onScheduleCreate}
                  onScheduleDelete={onScheduleDelete}
                />
              ))}
            </div>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="bg-gray-50 border-t border-gray-300 p-2 text-xs">
        <div className="flex gap-4">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 border border-gray-300 bg-white"></div>
            <span>Empty Slot</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 border border-green-500 bg-green-50"></div>
            <span>Scheduled</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 border border-red-500 bg-red-50"></div>
            <span>Conflict</span>
          </div>
          <div className="flex items-center gap-1">
            <span>S1:1, S1:2, S2:1, S2:2 = Shift:Slot</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductionGrid;