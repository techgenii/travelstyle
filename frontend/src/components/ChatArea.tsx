import React, { useState, useRef, useEffect } from 'react';
import { Plus, SlidersHorizontal, Mic, Activity, Send, Menu, Lightbulb } from 'lucide-react';
import { ChatMessage as ChatMessageType, User as UserType } from '../types';
import ChatMessage from './ChatMessage';
import TypingIndicator from './TypingIndicator';

interface ChatAreaProps {
  messages: ChatMessageType[];
  onSendMessage: (content: string) => void;
  isTyping: boolean;
  user: UserType;
  sessionGreeting: string;
}

const ChatArea: React.FC<ChatAreaProps> = ({
  messages,
  onSendMessage,
  isTyping,
  user,
  sessionGreeting
}) => {
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const subheader = "Your complete travel companion for smart packing, local dress codes, weather insights, activity planning, and currency conversions.";

  const proTips = [
    "Pack versatile clothing items that can be mixed and matched for different occasions.",
    "Always carry a portable charger for your devices, especially when traveling.",
    "Research local customs and etiquette to ensure a respectful travel experience.",
    "Use packing cubes to organize your luggage and maximize space.",
    "Learn a few basic phrases in the local language – it goes a long way!",
    "Ask me about exchange rates! Try: 'How much is 50 dollars in euros?'"
  ];

  const placeholders = [
    "What should I pack for a week in Thailand?",
    "Help me pack light for a business trip to London",
    "How much is 50 dollars in euros?",
    "What's appropriate to wear in Dubai?",
    "What's the weather like in Bali in March?",
    "What are the best activities in Rome?",
    "Convert 100 USD to Japanese yen",
    "How should I dress for temples in Thailand?",
    "Should I expect rain in London next week?",
    "Things to do in Bangkok for 3 days"
  ];

  const [currentProTip] = useState(() => proTips[Math.floor(Math.random() * proTips.length)]);
  const [currentPlaceholder] = useState(() => placeholders[Math.floor(Math.random() * placeholders.length)]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim()) {
      onSendMessage(inputValue.trim());
      setInputValue('');
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-background">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto pt-16 pl-16 pr-4 pb-32">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full max-w-3xl mx-auto text-center px-6">
            {/* Hamburger Menu Icon */}
            <div className="absolute top-6 left-6">
              <Menu className="w-6 h-6 text-text-secondary opacity-50" />
            </div>

            {/* Main Greeting */}
            <h1 className="text-5xl font-bold text-text-primary mb-6 leading-tight">
              {sessionGreeting}, {user.firstName}
            </h1>

            {/* Subheader */}
            <p className="text-xl text-text-secondary mb-12 leading-relaxed max-w-2xl">
              {subheader}
            </p>

            {/* Pro Tip */}
            <p className="text-lg text-text-primary leading-relaxed max-w-2xl mb-12">
              💡 {currentProTip}
            </p>

            {/* Input Field */}
            <div className="w-full max-w-2xl">
              <form onSubmit={handleSubmit} className="relative">
                <input
                  ref={inputRef}
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder={currentPlaceholder}
                  className="w-full px-6 py-4 text-lg border border-border bg-surface text-text-primary rounded-2xl focus:ring-2 focus:ring-secondary focus:border-transparent transition-all duration-300 pr-14 shadow-sm hover:shadow-md placeholder-text-secondary"
                  disabled={isTyping}
                />
                <button
                  type="submit"
                  disabled={isTyping || !inputValue.trim()}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 w-8 h-8 bg-secondary text-background rounded-full flex items-center justify-center hover:bg-primary disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
                >
                  <Send className="w-4 h-4" />
                </button>
              </form>
            </div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto">
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {isTyping && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area - Only show when there are messages */}
      {messages.length > 0 && (
        <div className="fixed inset-x-0 bottom-0 p-4 bg-transparent z-10 flex justify-center">
          <form onSubmit={handleSubmit} className="w-full max-w-2xl flex items-center bg-surface rounded-full shadow-lg px-4 py-3 border border-border">
            {/* Left side buttons */}
            <div className="flex items-center space-x-2 mr-3">
              <button
                type="button"
                className="w-8 h-8 flex items-center justify-center text-text-secondary hover:text-text-primary transition-colors duration-300"
              >
                <Plus className="w-5 h-5" />
              </button>
              <button
                type="button"
                className="flex items-center space-x-1 px-2 py-1 text-text-secondary hover:text-text-primary transition-colors duration-300"
              >
                <SlidersHorizontal className="w-4 h-4" />
                <span className="text-sm font-medium">Tools</span>
              </button>
            </div>
            
            {/* Input field */}
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask anything"
              className="flex-1 outline-none text-lg bg-transparent text-text-primary placeholder-text-secondary"
              disabled={isTyping}
            />
            
            {/* Right side buttons */}
            <div className="flex items-center space-x-2 ml-3">
              <button
                type="button"
                className="w-8 h-8 flex items-center justify-center text-text-secondary hover:text-text-primary transition-colors duration-300"
              >
                <Mic className="w-5 h-5" />
              </button>
              <button
                type="button"
                className="w-8 h-8 flex items-center justify-center text-text-secondary hover:text-text-primary transition-colors duration-300"
              >
                <Activity className="w-5 h-5" />
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default ChatArea;