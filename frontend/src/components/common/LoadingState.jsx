import React from 'react';

export default function LoadingState({ title = 'Loading...', subtitle, pulse = true }) {
  return (
    <div className="modern-card text-center">
      <div className="flex items-center justify-between">
        <div className="text-left">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-lg flex items-center justify-center">
              <span className="text-white text-sm">📊</span>
            </div>
            <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
          </div>
          {subtitle && <p className="text-gray-600">{subtitle}</p>}
        </div>
        {pulse && <div className="loading-pulse w-16 h-16 rounded-full"></div>}
      </div>
    </div>
  );
}
