import React from 'react';

export default function StatusHeader({ title, description, icon = '📋' }) {
  return (
    <div className="text-center mb-8">
      <h2 className="text-3xl font-bold text-gray-900 mb-3">
        <span className="mr-2">{icon}</span>
        {title}
      </h2>
      {description && (
        <p className="text-lg text-gray-600">{description}</p>
      )}
    </div>
  );
}
