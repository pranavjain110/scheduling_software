import { useState, useEffect, useMemo, useCallback } from 'react';
import apiService from '../services/api';

const Dashboard = ({ 
  parts = [], 
  machines = [], 
  schedules = [], 
  selectedDateRange
}) => {
  const [monthlyPlans, setMonthlyPlans] = useState([]);
  const [conflicts, setConflicts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    machine: '',
    part: '',
    dateRange: selectedDateRange
  });

  const loadConflictsForDateRange = useCallback(async () => {
    try {
      const startDate = new Date(selectedDateRange.start);
      const endDate = new Date(selectedDateRange.end);
      const allConflicts = [];

      // Get conflicts for each day in the range
      for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
        const dateStr = d.toISOString().split('T')[0];
        try {
          const dayConflicts = await apiService.getConflictsByDate(dateStr);
          if (dayConflicts.conflicts && dayConflicts.conflicts.length > 0) {
            allConflicts.push(...dayConflicts.conflicts);
          }
        } catch (error) {
          // Continue if no conflicts for this date - ignore error
          void error; // Explicitly acknowledge we're ignoring the error
          console.debug('No conflicts for date:', dateStr);
        }
      }
      
      setConflicts(allConflicts);
    } catch (error) {
      console.error('Error loading conflicts:', error);
    }
  }, [selectedDateRange]);

  const loadDashboardData = useCallback(async () => {
    setLoading(true);
    try {
      const [monthlyData] = await Promise.all([
        apiService.getMonthlyPlans()
      ]);
      
      setMonthlyPlans(monthlyData);

      // Load conflicts for the date range
      await loadConflictsForDateRange();
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  }, [loadConflictsForDateRange]);

  // Load additional dashboard data
  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  // Calculate machine utilization
  const machineUtilization = useMemo(() => {
    const utilization = {};
    
    machines.forEach(machine => {
      const machineSchedules = schedules.filter(s => s.machine_id === machine.machine_id);
      
      // Calculate utilization based on date range
      const startDate = new Date(selectedDateRange.start);
      const endDate = new Date(selectedDateRange.end);
      const dayCount = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24)) + 1;
      
      // Each day has 4 slots (2 shifts * 2 slots each)
      const totalSlots = dayCount * 4;
      const usedSlots = machineSchedules.length;
      
      utilization[machine.machine_id] = {
        machine,
        usedSlots,
        totalSlots,
        utilizationPercentage: totalSlots > 0 ? Math.round((usedSlots / totalSlots) * 100) : 0,
        scheduledOperations: machineSchedules.length
      };
    });
    
    return utilization;
  }, [machines, schedules, selectedDateRange]);

  // Find delayed operations
  const delayedOperations = useMemo(() => {
    return schedules.filter(schedule => schedule.status === 'delayed');
  }, [schedules]);

  // Calculate forecast vs actual
  const forecastVsActual = useMemo(() => {
    const comparison = {};
    
    // Group monthly plans by part
    monthlyPlans.forEach(plan => {
      const partId = plan.part_id;
      if (!comparison[partId]) {
        comparison[partId] = {
          part: parts.find(p => p.part_id === partId),
          planned: 0,
          actual: 0,
          variance: 0
        };
      }
      comparison[partId].planned += plan.planned_quantity || 0;
    });

    // Calculate actual production from completed schedules
    schedules
      .filter(schedule => schedule.status === 'completed')
      .forEach(schedule => {
        const partId = schedule.part_id;
        if (comparison[partId]) {
          comparison[partId].actual += schedule.quantity_scheduled || 0;
        }
      });

    // Calculate variance
    Object.keys(comparison).forEach(partId => {
      const data = comparison[partId];
      data.variance = data.actual - data.planned;
      data.variancePercentage = data.planned > 0 
        ? Math.round(((data.actual - data.planned) / data.planned) * 100) 
        : 0;
    });

    return comparison;
  }, [monthlyPlans, schedules, parts]);

  // Filter data based on current filters
  const filteredData = useMemo(() => {
    let filteredSchedules = schedules;
    let filteredUtilization = machineUtilization;

    if (filters.machine) {
      filteredSchedules = filteredSchedules.filter(s => s.machine_id === parseInt(filters.machine));
      filteredUtilization = Object.fromEntries(
        Object.entries(machineUtilization).filter(([machineId]) => machineId === filters.machine)
      );
    }

    if (filters.part) {
      filteredSchedules = filteredSchedules.filter(s => s.part_id === parseInt(filters.part));
    }

    return {
      schedules: filteredSchedules,
      utilization: filteredUtilization
    };
  }, [schedules, machineUtilization, filters]);

  const handleFilterChange = (filterType, value) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-600">Loading dashboard data...</div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Dashboard Header */}
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-gray-800 mb-2">Production Dashboard</h2>
        <p className="text-gray-600">
          Machine utilization, production progress, and conflict monitoring for {selectedDateRange.start} to {selectedDateRange.end}
        </p>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">Filters</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Machine</label>
            <select
              value={filters.machine}
              onChange={(e) => handleFilterChange('machine', e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
            >
              <option value="">All Machines</option>
              {machines.map(machine => (
                <option key={machine.machine_id} value={machine.machine_id}>
                  {machine.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Part</label>
            <select
              value={filters.part}
              onChange={(e) => handleFilterChange('part', e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
            >
              <option value="">All Parts</option>
              {parts.map(part => (
                <option key={part.part_id} value={part.part_id}>
                  {part.name}
                </option>
              ))}
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={() => setFilters({ machine: '', part: '', dateRange: selectedDateRange })}
              className="px-4 py-2 bg-gray-500 text-white rounded-md text-sm hover:bg-gray-600"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Key Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
        {/* Total Schedules */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Schedules</p>
              <p className="text-2xl font-bold text-gray-900">{filteredData.schedules.length}</p>
            </div>
          </div>
        </div>

        {/* Active Machines */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active Machines</p>
              <p className="text-2xl font-bold text-gray-900">{Object.keys(filteredData.utilization).length}</p>
            </div>
          </div>
        </div>

        {/* Delayed Operations */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 rounded-lg">
              <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Delayed Operations</p>
              <p className="text-2xl font-bold text-red-600">{delayedOperations.length}</p>
            </div>
          </div>
        </div>

        {/* Conflicts */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 15.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Conflicts</p>
              <p className="text-2xl font-bold text-yellow-600">{conflicts.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Machine Utilization */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">Machine Utilization</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Object.values(filteredData.utilization).map(({ machine, usedSlots, totalSlots, utilizationPercentage }) => (
            <div key={machine.machine_id} className="border border-gray-200 rounded-lg p-4">
              <div className="flex justify-between items-center mb-2">
                <h4 className="font-medium text-gray-800">{machine.name}</h4>
                <span className="text-sm text-gray-600">{machine.type}</span>
              </div>
              <div className="mb-2">
                <div className="flex justify-between text-sm text-gray-600 mb-1">
                  <span>Utilization</span>
                  <span>{utilizationPercentage}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${
                      utilizationPercentage >= 80 ? 'bg-red-500' : 
                      utilizationPercentage >= 60 ? 'bg-yellow-500' : 
                      'bg-green-500'
                    }`}
                    style={{ width: `${utilizationPercentage}%` }}
                  ></div>
                </div>
              </div>
              <div className="text-xs text-gray-500">
                {usedSlots} / {totalSlots} slots used
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Two Column Layout for remaining sections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Delayed Operations */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-xl font-semibold text-gray-800 mb-4">Delayed Operations</h3>
          {delayedOperations.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No delayed operations</p>
          ) : (
            <div className="space-y-3">
              {delayedOperations.slice(0, 5).map(schedule => {
                const part = parts.find(p => p.part_id === schedule.part_id);
                const machine = machines.find(m => m.machine_id === schedule.machine_id);
                return (
                  <div key={schedule.schedule_id} className="border border-red-200 rounded-lg p-3 bg-red-50">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-medium text-gray-800">
                          {part?.name || `Part ${schedule.part_id}`}
                        </p>
                        <p className="text-sm text-gray-600">
                          Machine: {machine?.name || `Machine ${schedule.machine_id}`}
                        </p>
                        <p className="text-sm text-gray-600">
                          Date: {schedule.date} | Shift: {schedule.shift_number} | Slot: {schedule.slot_number}
                        </p>
                      </div>
                      <span className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full">
                        Delayed
                      </span>
                    </div>
                  </div>
                );
              })}
              {delayedOperations.length > 5 && (
                <p className="text-center text-gray-500 text-sm">
                  And {delayedOperations.length - 5} more delayed operations...
                </p>
              )}
            </div>
          )}
        </div>

        {/* Conflicts Warning */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-xl font-semibold text-gray-800 mb-4">Scheduling Conflicts</h3>
          {conflicts.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No scheduling conflicts</p>
          ) : (
            <div className="space-y-3">
              {conflicts.slice(0, 5).map((conflict, index) => (
                <div key={index} className="border border-yellow-200 rounded-lg p-3 bg-yellow-50">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium text-gray-800">
                        Machine {conflict.slot_info?.machine_id}
                      </p>
                      <p className="text-sm text-gray-600">
                        Date: {conflict.slot_info?.date} | 
                        Shift: {conflict.slot_info?.shift_number} | 
                        Slot: {conflict.slot_info?.slot_number}
                      </p>
                      <p className="text-sm text-gray-600">
                        {conflict.conflicting_schedules?.length || 0} overlapping schedules
                      </p>
                    </div>
                    <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full">
                      Conflict
                    </span>
                  </div>
                </div>
              ))}
              {conflicts.length > 5 && (
                <p className="text-center text-gray-500 text-sm">
                  And {conflicts.length - 5} more conflicts...
                </p>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Forecast vs Actual Production */}
      <div className="bg-white rounded-lg shadow-sm p-6 mt-6">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">Forecast vs Actual Production</h3>
        {Object.keys(forecastVsActual).length === 0 ? (
          <p className="text-gray-500 text-center py-8">No production data available</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Part
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Planned
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actual
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Variance
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Performance
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {Object.values(forecastVsActual).map(({ part, planned, actual, variance, variancePercentage }) => (
                  <tr key={part?.part_id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {part?.name || 'Unknown Part'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {planned}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {actual}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={variance >= 0 ? 'text-green-600' : 'text-red-600'}>
                        {variance >= 0 ? '+' : ''}{variance}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        variancePercentage >= 0 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {variancePercentage >= 0 ? '+' : ''}{variancePercentage}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;