const API_BASE_URL = 'http://127.0.0.1:5000';

class ApiService {
  // Utility method for making API calls
  async makeRequest(url, options = {}) {
    try {
      const response = await fetch(`${API_BASE_URL}${url}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed for ${url}:`, error);
      throw error;
    }
  }

  // Parts API
  async getParts() {
    return this.makeRequest('/parts');
  }

  // Machines API
  async getMachines() {
    return this.makeRequest('/machines');
  }

  // Operations API
  async getOperations(partId = null) {
    const url = partId ? `/operations?part_id=${partId}` : '/operations';
    return this.makeRequest(url);
  }

  // Production Schedules API
  async getProductionSchedules(filters = {}) {
    const params = new URLSearchParams();
    if (filters.date) params.append('date', filters.date);
    if (filters.machine_id) params.append('machine_id', filters.machine_id);
    if (filters.part_id) params.append('part_id', filters.part_id);
    
    const url = `/production-schedules${params.toString() ? `?${params.toString()}` : ''}`;
    return this.makeRequest(url);
  }

  async createProductionSchedule(scheduleData) {
    return this.makeRequest('/production-schedules', {
      method: 'POST',
      body: JSON.stringify(scheduleData),
    });
  }

  async updateProductionSchedule(scheduleId, scheduleData) {
    return this.makeRequest(`/production-schedules/${scheduleId}`, {
      method: 'PUT',
      body: JSON.stringify(scheduleData),
    });
  }

  async deleteProductionSchedule(scheduleId) {
    return this.makeRequest(`/production-schedules/${scheduleId}`, {
      method: 'DELETE',
    });
  }

  // Conflict checking
  async checkSlotConflicts(slotData) {
    return this.makeRequest('/production-schedules/conflicts/check-slot', {
      method: 'POST',
      body: JSON.stringify(slotData),
    });
  }

  // Companies API
  async getCompanies() {
    return this.makeRequest('/companies');
  }
}

// Export a singleton instance
export default new ApiService();