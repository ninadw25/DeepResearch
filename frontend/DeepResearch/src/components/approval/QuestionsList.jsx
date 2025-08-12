import React from 'react';

export default function QuestionsList({ questions, onChange, onRemove }) {
  return (
    <div className="space-y-4 mb-8">
      <h3 className="text-xl font-semibold text-gray-900 mb-4">Research Questions</h3>
      {questions.map((question, index) => (
        <div key={index} className="flex items-start space-x-3">
          <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mt-1">
            <span className="text-sm font-semibold text-blue-600">{index + 1}</span>
          </div>
          <div className="flex-1">
            <textarea
              value={question}
              onChange={(e) => onChange(index, e.target.value)}
              placeholder="Enter research question..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none transition-colors"
              rows={2}
            />
          </div>
          {questions.length > 1 && (
            <button
              onClick={() => onRemove(index)}
              className="flex-shrink-0 w-8 h-8 bg-red-100 hover:bg-red-200 rounded-full flex items-center justify-center mt-1 transition-colors"
              title="Remove question"
            >
              <svg className="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>
      ))}
    </div>
  );
}
