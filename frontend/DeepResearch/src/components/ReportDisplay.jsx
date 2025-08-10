import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeSanitize from 'rehype-sanitize';
import rehypeExternalLinks from 'rehype-external-links';
import api, { hasValidReport } from '../services/api';

// Modern Markdown renderer with better styling
const Markdown = ({ children }) => (
  <ReactMarkdown
    remarkPlugins={[remarkGfm]}
    rehypePlugins={[
      [rehypeExternalLinks, { target: '_blank', rel: ['nofollow', 'noopener', 'noreferrer'] }],
      rehypeSanitize
    ]}
    components={{
      code({ inline, className, children, ...props }) {
        if (inline) {
          return <code className="bg-blue-100 text-blue-800 px-2 py-1 rounded-md text-sm font-mono" {...props}>{children}</code>;
        }
        return (
          <pre className="bg-gray-900 text-gray-100 p-4 rounded-xl overflow-auto my-4 shadow-inner">
            <code className={className} {...props}>{children}</code>
          </pre>
        );
      },
      a({ node, ...props }) {
        return <a className="text-blue-600 hover:text-blue-800 underline font-medium transition-colors" {...props} />;
      },
      ul({ node, ...props }) {
        return <ul className="list-disc pl-6 space-y-2 my-4" {...props} />;
      },
      ol({ node, ...props }) {
        return <ol className="list-decimal pl-6 space-y-2 my-4" {...props} />;
      },
      h1({ node, ...props }) {
        return <h1 className="text-2xl font-bold text-gray-900 mb-4 mt-6" {...props} />;
      },
      h2({ node, ...props }) {
        return <h2 className="text-xl font-semibold text-gray-900 mb-3 mt-5" {...props} />;
      },
      h3({ node, ...props }) {
        return <h3 className="text-lg font-semibold text-gray-900 mb-3 mt-4" {...props} />;
      },
      p({ node, ...props }) {
        return <p className="text-gray-700 leading-relaxed mb-4" {...props} />;
      },
      blockquote({ node, ...props }) {
        return <blockquote className="border-l-4 border-blue-500 pl-4 italic text-gray-600 my-4 bg-blue-50 py-2 rounded-r-lg" {...props} />;
      }
    }}
  >
    {typeof children === 'string' ? children : String(children ?? '')}
  </ReactMarkdown>
);

export default function ReportDisplay({ taskId, onReset }) {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState('Initializing...');

  useEffect(() => {
    if (!taskId) return;
    
    const fetchResults = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const data = await api.getResults(taskId, {
          onProgress: setProgress
        });
        
        setResults(data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching results:', err);
        setError(err.message || 'Failed to fetch results');
        setLoading(false);
      }
    };

    fetchResults();
  }, [taskId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-4">
        <div className="max-w-6xl mx-auto space-y-8">
          {/* Header */}
          <div className="modern-card">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-lg flex items-center justify-center">
                    <span className="text-white text-sm">📊</span>
                  </div>
                  <h1 className="text-2xl font-bold text-gray-900">Research in Progress</h1>
                </div>
                <p className="text-gray-600">{progress}</p>
              </div>
              <div className="loading-pulse w-16 h-16 rounded-full"></div>
            </div>
          </div>

          {/* Loading Cards */}
          <div className="space-y-6">
            <div className="loading-pulse modern-card h-64"></div>
            <div className="loading-pulse modern-card h-48"></div>
            <div className="loading-pulse modern-card h-56"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-4">
        <div className="max-w-4xl mx-auto">
          <div className="error-card text-center">
            <div className="text-red-500 text-6xl mb-4">⚠️</div>
            <h2 className="text-2xl font-bold text-red-900 mb-4">Research Failed</h2>
            <p className="text-red-700 mb-6">{error}</p>
            <button 
              onClick={onReset}
              className="btn-primary bg-gradient-to-r from-red-500 to-red-600"
            >
              Start New Research
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-4">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="modern-card">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl flex items-center justify-center shadow-lg">
                  <span className="text-white text-lg">📊</span>
                </div>
                <h1 className="text-3xl font-bold text-gray-900">Research Report</h1>
              </div>
              <p className="text-gray-600 text-lg">Comprehensive analysis completed</p>
            </div>
            <button 
              onClick={onReset}
              className="btn-secondary"
            >
              🔄 New Research
            </button>
          </div>
        </div>

        {/* Original Query */}
        <div className="modern-card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <span className="text-blue-500">❓</span>
            Original Research Question
          </h2>
          <div className="bg-blue-50/80 backdrop-blur-sm rounded-xl p-6 border border-blue-200/50">
            <p className="text-gray-800 text-lg italic leading-relaxed">
              "{results?.original_query || 'No query provided'}"
            </p>
          </div>
        </div>

        {/* Executive Summary */}
        <div className="report-summary-card">
          <h2 className="text-xl font-semibold text-gray-900 mb-6 flex items-center gap-2">
            <span className="text-purple-500">📋</span>
            Executive Summary
          </h2>
          <div className="prose-modern">
            <Markdown>{results?.summary || results?.final_report || 'Summary not available'}</Markdown>
          </div>
        </div>

        {/* Detailed Findings */}
        <div className="modern-card">
          <h2 className="text-xl font-semibold text-gray-900 mb-6 flex items-center gap-2">
            <span className="text-emerald-500">🔍</span>
            Detailed Findings
          </h2>
          
          <div className="space-y-6">
            {(results?.findings || []).map((finding, idx) => {
              const items = Array.isArray(finding?.results) ? finding.results : [];
              return (
                <div key={idx} className="report-finding-card">
                  <div className="flex items-start gap-3 mb-4">
                    <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-lg flex items-center justify-center flex-shrink-0 mt-1">
                      <span className="text-white text-sm font-bold">{idx + 1}</span>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 leading-tight">
                      {finding?.question || `Finding ${idx + 1}`}
                    </h3>
                  </div>
                  
                  <div className="ml-11 space-y-4">
                    {items.length === 0 ? (
                      <div className="text-gray-500 italic bg-gray-50 rounded-lg p-4 text-center">
                        No research results found for this question.
                      </div>
                    ) : (
                      items.map((result, i) => {
                        const text = typeof result === 'string' 
                          ? result 
                          : result?.content || result?.text || result?.summary || '';
                        
                        return (
                          <div key={i} className="bg-white/80 rounded-xl p-6 border border-gray-100 shadow-sm">
                            <div className="prose-modern">
                              <Markdown>{text}</Markdown>
                            </div>
                            {result?.url && (
                              <div className="mt-4 pt-4 border-t border-gray-100">
                                <a
                                  href={result.url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-800 font-medium transition-colors"
                                >
                                  <span className="text-sm">🔗</span>
                                  View Source
                                </a>
                              </div>
                            )}
                          </div>
                        );
                      })
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Footer */}
        <div className="modern-card text-center">
          <p className="text-gray-500 text-sm">
            Report generated by Deep Research AI Agent • {new Date().toLocaleDateString()}
          </p>
        </div>
      </div>
    </div>
  );
}
