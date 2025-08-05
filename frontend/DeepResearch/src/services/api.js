const API_BASE_URL = 'http://127.0.0.1:8000';

export const api = {
  // Start a new research task
  async startResearch(query) {
    const response = await fetch(`${API_BASE_URL}/research`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to start research: ${response.statusText}`);
    }
    
    return response.json();
  },

  // Get task status and research questions
  async getTaskStatus(taskId) {
    const response = await fetch(`${API_BASE_URL}/status/${taskId}`);
    
    if (!response.ok) {
      throw new Error(`Failed to get task status: ${response.statusText}`);
    }
    
    return response.json();
  },

  // Resume task with approved research questions
  async resumeTask(taskId, researchQuestions) {
    const response = await fetch(`${API_BASE_URL}/resume/${taskId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ research_questions: researchQuestions }),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to resume task: ${response.statusText}`);
    }
    
    return response.json();
  },

  // Get final results
  async getResults(taskId) {
    const response = await fetch(`${API_BASE_URL}/results/${taskId}`);
    
    if (!response.ok) {
      throw new Error(`Failed to get results: ${response.statusText}`);
    }
    
    return response.json();
  },
};
