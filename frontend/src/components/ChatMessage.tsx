import React, { useState } from 'react';
import { Bot, User, ThumbsUp, ThumbsDown } from 'lucide-react';
import { ChatMessage as ChatMessageType } from '../types';

interface ChatMessageProps {
  message: ChatMessageType;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isAI = message.sender === 'ai';
  const [feedbackStatus, setFeedbackStatus] = useState<'liked' | 'disliked' | null>(null);

  const handleThumbsUp = () => {
    const newStatus = feedbackStatus === 'liked' ? null : 'liked';
    setFeedbackStatus(newStatus);
    console.log('Thumbs up for message:', message.id, 'Status:', newStatus);
  };

  const handleThumbsDown = () => {
    const newStatus = feedbackStatus === 'disliked' ? null : 'disliked';
    setFeedbackStatus(newStatus);
    console.log('Thumbs down for message:', message.id, 'Status:', newStatus);
  };
  
  return (
    <div className={`flex ${isAI ? 'justify-start' : 'justify-end'} mb-4`}>
      <div className={`flex max-w-md lg:max-w-xl xl:max-w-2xl ${isAI ? 'flex-row' : 'flex-row-reverse'}`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 ${isAI ? 'mr-3' : 'ml-3'}`}>
          <div className={`
            w-8 h-8 rounded-full flex items-center justify-center
            ${isAI ? 'bg-gradient-to-br from-primary to-secondary' : 'bg-accent'}
          `}>
            {isAI ? (
              <Bot className="w-4 h-4 text-background" />
            ) : (
              <User className="w-4 h-4 text-background" />
            )}
          </div>
        </div>

        {/* Message bubble */}
        <div className={`
          px-5 py-4 rounded-3xl shadow-md
          ${isAI 
            ? 'bg-surface border border-border text-text-primary' 
            : 'bg-gradient-to-r from-primary to-secondary text-background'
          }
        `}>
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
          
          {/* Feedback buttons - only for AI messages */}
          {isAI && (
            <div className="flex items-center space-x-2 mt-3 mb-2">
              <button
                onClick={handleThumbsUp}
                className={`
                  w-6 h-6 flex items-center justify-center rounded-full transition-all duration-200 group
                  ${feedbackStatus === 'liked' 
                    ? 'bg-success-light' 
                    : 'hover:bg-accent-light'
                  }
                `}
              >
                <ThumbsUp className={`
                  w-4 h-4 transition-colors duration-200
                  ${feedbackStatus === 'liked' 
                    ? 'text-success fill-current' 
                    : 'text-text-secondary group-hover:text-success'
                  }
                `} />
              </button>
              <button
                onClick={handleThumbsDown}
                className={`
                  w-6 h-6 flex items-center justify-center rounded-full transition-all duration-200 group
                  ${feedbackStatus === 'disliked' 
                    ? 'bg-error-light' 
                    : 'hover:bg-accent-light'
                  }
                `}
              >
                <ThumbsDown className={`
                  w-4 h-4 transition-colors duration-200
                  ${feedbackStatus === 'disliked' 
                    ? 'text-error fill-current' 
                    : 'text-text-secondary group-hover:text-error'
                  }
                `} />
              </button>
            </div>
          )}
          
          <div className={`text-xs mt-2 ${isAI ? 'text-text-secondary' : 'text-background opacity-75'}`}>
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;