import { useState, useEffect } from 'react';
import ProductionGrid from './ProductionGrid';
import GanttChart from './GanttChart';
import apiService from '../services/api';

const ProductionPlanner = () => {
  const [currentView, setCurrentView] = useState('grid');
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
    } catch (error) {
      console.error('Error loading data:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleScheduleCreate = async (scheduleData) => {
    try {
      const newSchedule = await apiService.createProductionSchedule(scheduleData);
      
      // Update schedules state
      setSchedules(prev => [...prev, newSchedule]);
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
        <div className="text-lg">Loading production planning data...</div>
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
    <div className="h-full flex flex-col">
      {/* View Toggle and Controls */}
      <div className="bg-white border-b border-gray-300 p-4">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold text-gray-800">CNC Workshop Production Planning</h1>
          <div className="flex bg-gray-200 rounded-lg p-1">
            <button
              onClick={() => setCurrentView('grid')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                currentView === 'grid'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              📊 Grid View
            </button>
            <button
              onClick={() => setCurrentView('gantt')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                currentView === 'gantt'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              📈 Gantt Chart
            </button>
          </div>
        </div>
        
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
      
      {/* View Content */}
      <div className="flex-1 overflow-hidden">
        {currentView === 'grid' ? (
          <ProductionGrid 
            parts={parts}
            machines={machines}
            operations={operations}
            schedules={schedules}
            selectedDateRange={selectedDateRange}
            onScheduleCreate={handleScheduleCreate}
            onScheduleUpdate={handleScheduleUpdate}
            onScheduleDelete={handleScheduleDelete}
            onDateRangeChange={handleDateRangeChange}
            loadData={loadData}
          />
        ) : (
          <GanttChart
            parts={parts}
            machines={machines}
            operations={operations}
            schedules={schedules}
            selectedDateRange={selectedDateRange}
          />
        )}
      </div>
    </div>
  );
};

export default ProductionPlanner;