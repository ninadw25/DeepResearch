import React from 'react';
import Markdown from './Markdown';

function FindingItem({ index, finding }) {
  const items = Array.isArray(finding?.results) ? finding.results : [];
  return (
    <div className="report-finding-card">
      <div className="flex items-start gap-3 mb-4">
        <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-lg flex items-center justify-center flex-shrink-0 mt-1">
          <span className="text-white text-sm font-bold">{index + 1}</span>
        </div>
        <h3 className="text-lg font-semibold text-gray-900 leading-tight">
          {finding?.question || `Finding ${index + 1}`}
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
}

export default function FindingsList({ findings = [] }) {
  return (
    <div className="space-y-6">
      {findings.map((finding, idx) => (
        <FindingItem key={idx} index={idx} finding={finding} />
      ))}
    </div>
  );
}
