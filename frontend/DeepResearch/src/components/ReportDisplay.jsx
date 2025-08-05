import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function ReportDisplay({ taskId, onReset }) {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [progress, setProgress] = useState('Researching...');

  useEffect(() => {
    pollForResults();
  }, [taskId]);

  const pollForResults = async () => {
    try {
      setLoading(true);
      setError('');
      
      const messages = [
        'Researching your questions...',
        'Analyzing findings...',
        'Gathering citations...',
        'Generating comprehensive report...',
        'Finalizing results...'
      ];
      
      let messageIndex = 0;
      
      const messageInterval = setInterval(() => {
        messageIndex = (messageIndex + 1) % messages.length;
        setProgress(messages[messageIndex]);
      }, 3000);

      // Poll for results
      const pollInterval = setInterval(async () => {
        try {
          const statusResponse = await api.getTaskStatus(taskId);
          
          if (statusResponse.status === 'COMPLETE') {
            clearInterval(pollInterval);
            clearInterval(messageInterval);
            
            // Fetch the final results
            const results = await api.getResults(taskId);
            setReport(results);
            setLoading(false);
          }
        } catch (err) {
          console.error('Error polling for results:', err);
          // Continue polling unless it's a critical error
        }
      }, 3000);

      // Clear intervals after 10 minutes to prevent infinite polling
      setTimeout(() => {
        clearInterval(pollInterval);
        clearInterval(messageInterval);
        if (loading) {
          setError('Research is taking longer than expected. Please try again.');
          setLoading(false);
        }
      }, 600000);

    } catch (err) {
      setError(err.message || 'Failed to fetch results');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="w-full max-w-4xl mx-auto animate-fade-in">
        <div className="bg-white rounded-2xl shadow-lg p-8 text-center">
          <div className="mb-6">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-blue-100 to-purple-100 rounded-full mb-6">
              <svg className="animate-spin w-10 h-10 text-blue-600" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
            <h2 className="text-3xl font-bold text-gray-900 mb-3">🔍 Deep Research in Progress</h2>
            <p className="text-xl text-gray-600 mb-2">{progress}</p>
            <p className="text-gray-500">This may take 2-5 minutes depending on the complexity of your research.</p>
          </div>
          
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6">
            <div className="flex items-center justify-center space-x-4 text-sm text-gray-600 mb-4">
              <div className="flex items-center">
                <div className="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                Searching multiple sources
              </div>
              <div className="flex items-center">
                <div className="w-2 h-2 bg-blue-400 rounded-full mr-2"></div>
                Analyzing content
              </div>
              <div className="flex items-center">
                <div className="w-2 h-2 bg-purple-400 rounded-full mr-2"></div>
                Synthesizing findings
              </div>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full animate-pulse" style={{width: '75%'}}></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full max-w-4xl mx-auto animate-fade-in">
        <div className="bg-white rounded-2xl shadow-lg p-8 text-center">
          <div className="text-red-400 mb-4">
            <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-3">Research Failed</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={onReset}
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
          >
            Start New Research
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-6xl mx-auto animate-fade-in">
      <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-8 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2">📊 Research Report</h1>
              <p className="text-blue-100 text-lg">Comprehensive analysis completed</p>
            </div>
            <button
              onClick={onReset}
              className="bg-white/20 hover:bg-white/30 text-white px-4 py-2 rounded-lg transition-colors flex items-center space-x-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <span>New Research</span>
            </button>
          </div>
        </div>

        <div className="p-8">
          {/* Original Query */}
          <div className="mb-8 p-6 bg-gray-50 rounded-lg">
            <h2 className="text-lg font-semibold text-gray-900 mb-2">Original Research Question</h2>
            <p className="text-gray-700 text-lg italic">"{report.original_query}"</p>
          </div>

          {/* Executive Summary */}
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
              <span className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-3 text-blue-600 text-sm font-bold">📋</span>
              Executive Summary
            </h2>
            <div className="prose max-w-none">
              <div className="bg-blue-50 rounded-lg p-6">
                <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">{report.summary}</p>
              </div>
            </div>
          </div>

          {/* Detailed Findings */}
          {report.findings && report.findings.length > 0 && (
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                <span className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center mr-3 text-green-600 text-sm font-bold">🔍</span>
                Detailed Findings
              </h2>
              <div className="space-y-6">
                {report.findings.map((finding, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg overflow-hidden">
                    <div className="bg-gray-50 px-6 py-3 border-b border-gray-200">
                      <h3 className="font-semibold text-gray-900 flex items-center">
                        <span className="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm mr-3">
                          {index + 1}
                        </span>
                        {finding.question}
                      </h3>
                    </div>
                    <div className="p-6">
                      <div className="prose max-w-none">
                        {Array.isArray(finding.results) ? (
                          <div className="space-y-3">
                            {finding.results.map((result, resultIndex) => (
                              <p key={resultIndex} className="text-gray-700 leading-relaxed">
                                {result}
                              </p>
                            ))}
                          </div>
                        ) : (
                          <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                            {finding.results}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Citations */}
          {report.citations && report.citations.length > 0 && (
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                <span className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center mr-3 text-purple-600 text-sm font-bold">📚</span>
                Sources & Citations
              </h2>
              <div className="bg-gray-50 rounded-lg p-6">
                <div className="grid gap-3">
                  {report.citations.map((citation, index) => (
                    <div key={index} className="flex items-start space-x-3">
                      <span className="flex-shrink-0 w-6 h-6 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-sm font-bold">
                        {index + 1}
                      </span>
                      <div className="flex-1">
                        {citation.source.startsWith('http') ? (
                          <a 
                            href={citation.source}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:text-blue-800 hover:underline break-all"
                          >
                            {citation.source}
                          </a>
                        ) : (
                          <span className="text-gray-700 break-all">{citation.source}</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Footer */}
          <div className="pt-6 border-t border-gray-200 text-center">
            <p className="text-gray-500 text-sm">
              Report generated by Deep Research AI Agent • {new Date().toLocaleDateString()}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
