import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import StatusHeader from './approval/StatusHeader';
import QuestionsList from './approval/QuestionsList';
import ErrorAlert from './common/ErrorAlert';

export default function ApprovalScreen({ taskId, onPlanApproved }) {
  const [researchQuestions, setResearchQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchResearchQuestions();
  }, [taskId]);

  const fetchResearchQuestions = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Poll for the research questions
      const pollInterval = setInterval(async () => {
        try {
          const response = await api.getTaskStatus(taskId);
          
          if (response.status === 'AWAITING_INPUT' && response.research_questions) {
            setResearchQuestions(response.research_questions);
            setLoading(false);
            clearInterval(pollInterval);
          } else if (response.status === 'COMPLETE') {
            // If already complete, go straight to results
            onPlanApproved();
            clearInterval(pollInterval);
          }
        } catch (err) {
          console.error('Error fetching questions:', err);
          setError('Failed to fetch research questions');
          setLoading(false);
          clearInterval(pollInterval);
        }
      }, 2000);

      // Clear interval after 30 seconds to prevent infinite polling
      setTimeout(() => {
        clearInterval(pollInterval);
        if (loading) {
          setError('Timeout waiting for research questions');
          setLoading(false);
        }
      }, 30000);

    } catch (err) {
      setError(err.message || 'Failed to fetch research questions');
      setLoading(false);
    }
  };

  const handleQuestionChange = (index, value) => {
    const updated = [...researchQuestions];
    updated[index] = value;
    setResearchQuestions(updated);
  };

  const addQuestion = () => {
    setResearchQuestions([...researchQuestions, '']);
  };

  const removeQuestion = (index) => {
    const updated = researchQuestions.filter((_, i) => i !== index);
    setResearchQuestions(updated);
  };

  const handleApprove = async () => {
    const validQuestions = researchQuestions.filter(q => q.trim());
    
    if (validQuestions.length === 0) {
      setError('Please provide at least one research question');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      await api.resumeTask(taskId, validQuestions);
      onPlanApproved();
    } catch (err) {
      setError(err.message || 'Failed to approve research plan');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="w-full max-w-4xl mx-auto animate-fade-in">
        <div className="bg-white rounded-2xl shadow-lg p-8 text-center">
          <div className="mb-6">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
              <svg className="animate-spin w-8 h-8 text-blue-600" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Generating Research Questions</h2>
            <p className="text-gray-600">Our AI is analyzing your query and generating comprehensive research questions...</p>
          </div>
          <div className="bg-blue-50 rounded-lg p-4">
            <p className="text-sm text-blue-700">This usually takes 10-30 seconds</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-4xl mx-auto animate-fade-in">
      <div className="bg-white rounded-2xl shadow-lg p-8">
        <StatusHeader 
          title="Review Research Plan" 
          description="Review and edit the generated research questions. You can modify, add, or remove questions as needed." 
        />

        <ErrorAlert message={error} className="mb-6" />

        <QuestionsList 
          questions={researchQuestions}
          onChange={handleQuestionChange}
          onRemove={removeQuestion}
        />

        {/* Add Question Button */}
  <div className="mb-8">
          <button
            onClick={addQuestion}
            className="flex items-center space-x-2 px-4 py-2 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-400 hover:bg-blue-50 transition-colors"
          >
            <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            <span className="text-gray-600">Add another question</span>
          </button>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-center space-x-4">
          <button
            onClick={handleApprove}
            disabled={submitting || researchQuestions.filter(q => q.trim()).length === 0}
            className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-semibold py-3 px-8 rounded-lg transition-colors duration-200 flex items-center"
          >
            {submitting ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Starting Research...
              </>
            ) : (
              <>
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Approve & Start Research
              </>
            )}
          </button>
        </div>

  {/* Info Box */}
        <div className="mt-8 bg-blue-50 rounded-lg p-4">
          <div className="flex items-start">
            <div className="text-blue-400 mr-3 mt-0.5">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
            <div>
              <h4 className="font-semibold text-blue-900 mb-1">What happens next?</h4>
              <p className="text-blue-700 text-sm">
                Once approved, our AI agent will research each question using multiple sources, analyze the findings, 
                and generate a comprehensive report with citations. This process typically takes 2-5 minutes.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
