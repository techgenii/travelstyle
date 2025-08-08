import React from 'react';
import { Bot } from 'lucide-react';

const TypingIndicator: React.FC = () => {
  return (
    <div className="flex justify-start mb-4">
      <div className="flex flex-row max-w-md lg:max-w-xl xl:max-w-2xl">
        {/* Avatar */}
        <div className="flex-shrink-0 mr-3">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
            <Bot className="w-4 h-4 text-background" />
          </div>
        </div>

        {/* Typing bubble */}
        <div className="px-5 py-4 bg-surface border border-border rounded-3xl shadow-md">
          <div className="flex space-x-1">
            <div className="w-2 h-2 bg-text-secondary rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
            <div className="w-2 h-2 bg-text-secondary rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
            <div className="w-2 h-2 bg-text-secondary rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;