import { useState, useEffect } from 'react';
import DayColumn from './DayColumn';
import apiService from '../services/api';

const ProductionGrid = () => {
  const [parts, setParts] = useState([]);
  const [machines, setMachines] = useState([]);
  const [operations, setOperations] = useState([]);
  const [schedules, setSchedules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedDateRange, setSelectedDateRange] = useState({
    start: new Date().toISOString().split('T')[0],
    end: new Date(Date.now() + 6 * 24 * 60 * 60 * 1000).toISOString().split('T')[0] // 7 days from today
  });

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

  // Load initial data
  useEffect(() => {
    loadData();
  }, [selectedDateRange]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const [partsData, machinesData, operationsData, schedulesData] = await Promise.all([
        apiService.getParts(),
        apiService.getMachines(),
        apiService.getOperations(),
        apiService.getProductionSchedules({
          // Could filter by date range if needed
        })
      ]);

      setParts(partsData);
      setMachines(machinesData);
      setOperations(operationsData);
      setSchedules(schedulesData);
    } catch (err) {
      setError(`Failed to load data: ${err.message}`);
      console.error('Error loading data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleScheduleCreate = async (scheduleData) => {
    try {
      const newSchedule = await apiService.createProductionSchedule(scheduleData);
      
      // Update schedules state
      setSchedules(prev => [...prev, newSchedule]);
      
      // Handle conflict warnings if any
      if (newSchedule.warnings?.conflicts_detected) {
        console.warn('Conflicts detected:', newSchedule.warnings.conflicts);
        // Could show a toast notification here
      }
      
      return newSchedule;
    } catch (error) {
      console.error('Error creating schedule:', error);
      throw error;
    }
  };

  const handleScheduleUpdate = async (scheduleId, scheduleData) => {
    try {
      const updatedSchedule = await apiService.updateProductionSchedule(scheduleId, scheduleData);
      
      // Update schedules state
      setSchedules(prev => 
        prev.map(s => s.schedule_id === scheduleId ? updatedSchedule : s)
      );
      
      // Handle conflict warnings if any
      if (updatedSchedule.warnings?.conflicts_detected) {
        console.warn('Conflicts detected:', updatedSchedule.warnings.conflicts);
        // Could show a toast notification here
      }
      
      return updatedSchedule;
    } catch (error) {
      console.error('Error updating schedule:', error);
      throw error;
    }
  };

  const handleScheduleDelete = async (scheduleId) => {
    try {
      await apiService.deleteProductionSchedule(scheduleId);
      
      // Update schedules state
      setSchedules(prev => prev.filter(s => s.schedule_id !== scheduleId));
    } catch (error) {
      console.error('Error deleting schedule:', error);
      throw error;
    }
  };

  const handleDateRangeChange = (field, value) => {
    setSelectedDateRange(prev => ({
      ...prev,
      [field]: value
    }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Loading production planning grid...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-red-600">
          <div className="text-lg font-semibold">Error</div>
          <div>{error}</div>
          <button 
            onClick={loadData}
            className="mt-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-300 p-4">
        <h1 className="text-2xl font-bold text-gray-800 mb-4">Production Planning Grid</h1>
        
        {/* Date range selector */}
        <div className="flex items-center gap-4 mb-4">
          <label className="text-sm font-medium text-gray-700">Date Range:</label>
          <input
            type="date"
            value={selectedDateRange.start}
            onChange={(e) => handleDateRangeChange('start', e.target.value)}
            className="border border-gray-300 rounded px-3 py-1 text-sm"
          />
          <span className="text-gray-500">to</span>
          <input
            type="date"
            value={selectedDateRange.end}
            onChange={(e) => handleDateRangeChange('end', e.target.value)}
            className="border border-gray-300 rounded px-3 py-1 text-sm"
          />
          <button
            onClick={loadData}
            className="px-4 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600"
          >
            Refresh
          </button>
        </div>

        {/* Stats */}
        <div className="flex gap-6 text-sm text-gray-600">
          <span>Parts: {parts.length}</span>
          <span>Machines: {machines.length}</span>
          <span>Scheduled Slots: {schedules.length}</span>
        </div>
      </div>

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
                  onScheduleUpdate={handleScheduleUpdate}
                  onScheduleCreate={handleScheduleCreate}
                  onScheduleDelete={handleScheduleDelete}
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