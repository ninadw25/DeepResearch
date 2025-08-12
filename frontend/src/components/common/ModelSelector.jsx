import React from 'react';

const MODEL_OPTIONS = [
  {
    id: 'groq',
    name: 'Groq (Llama)',
    description: 'Fast inference with Llama models',
    icon: '⚡'
  },
  {
    id: 'google',
    name: 'Google Gemini',
    description: 'Google\'s advanced AI model',
    icon: '🧠'
  },
  {
    id: 'ollama',
    name: 'Ollama (Local)',
    description: 'Run models locally with Ollama',
    icon: '🏠'
  },
  {
    id: 'openrouter',
    name: 'OpenRouter',
    description: 'Access to multiple model providers',
    icon: '🔀'
  }
];

export default function ModelSelector({ selectedModel, onModelChange, apiKey, onApiKeyChange }) {
  const selectedModelInfo = MODEL_OPTIONS.find(m => m.id === selectedModel);

  return (
    <div className="space-y-4">
      {/* Model Selection */}
      <div>
        <label htmlFor="model-select" className="block text-sm font-medium text-gray-700 mb-2">
          AI Model Provider
        </label>
        <select
          id="model-select"
          value={selectedModel}
          onChange={(e) => onModelChange(e.target.value)}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
        >
          {MODEL_OPTIONS.map((model) => (
            <option key={model.id} value={model.id}>
              {model.icon} {model.name} - {model.description}
            </option>
          ))}
        </select>
      </div>

      {/* API Key Input */}
      <div>
        <label htmlFor="api-key" className="block text-sm font-medium text-gray-700 mb-2">
          API Key (Optional)
          <span className="text-xs text-gray-500 ml-1">
            - Leave empty to use default configuration
          </span>
        </label>
        <div className="relative">
          <input
            id="api-key"
            type="password"
            value={apiKey}
            onChange={(e) => onApiKeyChange(e.target.value)}
            placeholder={`Enter your ${selectedModelInfo?.name || 'API'} key (optional)`}
            className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
          />
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
            <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          </div>
        </div>
      </div>

      {/* Info Box */}
      <div className="bg-blue-50 rounded-lg p-4">
        <div className="flex items-start">
          <div className="text-blue-400 mr-3 mt-0.5">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </div>
          <div>
            <h4 className="font-semibold text-blue-900 mb-1">Model Selection</h4>
            <p className="text-blue-700 text-sm">
              Choose your preferred AI model provider. If no API key is provided, the system will use the default configuration from environment variables.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
