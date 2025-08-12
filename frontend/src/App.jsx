import React, { useState } from 'react';
import ResearchForm from './components/ResearchForm';
import ApprovalScreen from './components/ApprovalScreen';
import ReportDisplay from './components/ReportDisplay';

export default function App() {
  const [taskId, setTaskId] = useState(null);
  const [stage, setStage] = useState('start'); // 'start', 'approval', 'results'

  const handleResearchStart = (newTaskId) => {
    setTaskId(newTaskId);
    setStage('approval');
  };
  
  const handlePlanApproved = () => {
    setStage('results');
  };
  
  const handleReset = () => {
    setTaskId(null);
    setStage('start');
  };

  const renderContent = () => {
    switch(stage) {
      case 'approval':
        return <ApprovalScreen taskId={taskId} onPlanApproved={handlePlanApproved} onReset={handleReset} />;
      case 'results':
        return <ReportDisplay taskId={taskId} onReset={handleReset} />;
      case 'start':
      default:
        return <ResearchForm onResearchStart={handleResearchStart} />;
    }
  };

  return (
    <div className="bg-gradient-to-br from-gray-50 to-blue-50 min-h-screen py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Progress Indicator */}
        {stage !== 'start' && (
          <div className="mb-8 flex justify-center">
            <div className="flex items-center space-x-4">
              <div className="flex items-center">
                <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center text-white text-sm font-bold">
                  ✓
                </div>
                <span className="ml-2 text-sm font-medium text-gray-700">Query Submitted</span>
              </div>
              <div className="w-8 h-0.5 bg-gray-300"></div>
              <div className="flex items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                  stage === 'approval' ? 'bg-blue-500 text-white' : 
                  stage === 'results' ? 'bg-green-500 text-white' : 'bg-gray-300 text-gray-600'
                }`}>
                  {stage === 'approval' ? '2' : '✓'}
                </div>
                <span className="ml-2 text-sm font-medium text-gray-700">Review Questions</span>
              </div>
              <div className="w-8 h-0.5 bg-gray-300"></div>
              <div className="flex items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                  stage === 'results' ? 'bg-blue-500 text-white' : 'bg-gray-300 text-gray-600'
                }`}>
                  3
                </div>
                <span className="ml-2 text-sm font-medium text-gray-700">View Results</span>
              </div>
            </div>
          </div>
        )}

        {/* Main Content */}
        <div className="flex justify-center">
          {renderContent()}
        </div>
      </div>
    </div>
  );
}
