import React, { useState } from 'react';
import { ArrowLeft, MessageSquarePlus, Search, Star, MessageSquare, X } from 'lucide-react';
import { Conversation } from '../types';

interface ChatHistoryPageProps {
  title: string;
  conversations: Conversation[];
  onSelectChat: (id: string) => void;
  onNewChat: () => void;
  onBack: () => void;
  showSearch?: boolean;
}

const ChatHistoryPage: React.FC<ChatHistoryPageProps> = ({
  title,
  conversations,
  onSelectChat,
  onNewChat,
  onBack,
  showSearch = true
}) => {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredConversations = conversations.filter(conversation =>
    conversation.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    conversation.lastMessage.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const formatTimeAgo = (timestamp: Date) => {
    const now = new Date();
    const diffInMs = now.getTime() - timestamp.getTime();
    const diffInMinutes = Math.floor(diffInMs / (1000 * 60));
    const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60));
    const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));
    
    if (diffInMinutes < 60) {
      return diffInMinutes <= 1 ? 'Just now' : `${diffInMinutes} minutes ago`;
    } else if (diffInHours < 24) {
      return diffInHours === 1 ? '1 hour ago' : `${diffInHours} hours ago`;
    }
    
    if (diffInDays === 0) {
      return 'Today';
    } else if (diffInDays === 1) {
      return 'Yesterday';
    } else if (diffInDays < 7) {
      return `${diffInDays} days ago`;
    } else if (diffInDays < 30) {
      const weeks = Math.floor(diffInDays / 7);
      return weeks === 1 ? '1 week ago' : `${weeks} weeks ago`;
    } else {
      const months = Math.floor(diffInDays / 30);
      return months === 1 ? '1 month ago' : `${months} months ago`;
    }
  };

  const getDisplayGroupHeader = (timestamp: Date) => {
    const now = new Date();
    const diffInMs = now.getTime() - timestamp.getTime();
    const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));
    
    if (diffInDays === 0) {
      return 'Today';
    } else if (diffInDays === 1) {
      return 'Yesterday';
    } else {
      return timestamp.toLocaleDateString('en-US', { month: 'long', day: 'numeric' });
    }
  };

  const getTagColor = (tag: string) => {
    const tagColors: { [key: string]: { bg: string; text: string } } = {
      'wardrobe': { bg: 'bg-primary-light', text: 'text-primary' },
      'style': { bg: 'bg-secondary-light', text: 'text-secondary' },
      'currency': { bg: 'bg-success-light', text: 'text-success' },
      'winter': { bg: 'bg-accent-light', text: 'text-accent' },
      'sports': { bg: 'bg-warning-light', text: 'text-warning' },
      'summer': { bg: 'bg-warning-light', text: 'text-warning' },
      'beach': { bg: 'bg-accent-light', text: 'text-accent' },
      'travel': { bg: 'bg-primary-light', text: 'text-primary' },
      'versatile': { bg: 'bg-secondary-light', text: 'text-secondary' },
      'formal': { bg: 'bg-accent-light', text: 'text-accent' }
    };
    
    return tagColors[tag] || { bg: 'bg-accent-light', text: 'text-accent' };
  };

  // Group conversations by date
  const groupedConversations = filteredConversations.reduce((groups, conversation) => {
    const dateKey = conversation.timestamp.toDateString();
    if (!groups[dateKey]) {
      groups[dateKey] = [];
    }
    groups[dateKey].push(conversation);
    return groups;
  }, {} as { [key: string]: Conversation[] });

  // Sort date groups by most recent first
  const sortedDateKeys = Object.keys(groupedConversations).sort((a, b) => 
    new Date(b).getTime() - new Date(a).getTime()
  );

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Header */}
      <div className="bg-surface border-b border-border px-4 lg:px-6 py-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-4">
              <button
                onClick={onBack}
                className="w-10 h-10 flex items-center justify-center rounded-xl hover:bg-accent-light transition-all duration-300"
              >
                <ArrowLeft className="w-5 h-5 text-text-secondary" />
              </button>
              <h1 className="text-3xl font-extrabold text-text-primary leading-tight">{title}</h1>
            </div>
            
            <button
              onClick={onNewChat}
              className="bg-gradient-to-r from-primary to-secondary text-background px-6 py-3 rounded-xl flex items-center space-x-2 hover:from-secondary hover:to-primary transition-all duration-300 shadow-lg hover:shadow-xl font-semibold"
            >
              <MessageSquarePlus className="w-4 h-4" />
              <span className="font-medium">New chat</span>
            </button>
          </div>

          {/* Search Bar */}
          {showSearch && (
            <div className="relative mb-6">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-text-secondary" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search your chats..."
                className="w-full pl-12 pr-4 py-3 border border-border bg-surface text-text-primary rounded-xl focus:ring-2 focus:ring-secondary focus:border-transparent transition-all duration-300 hover:bg-background focus:bg-background shadow-sm placeholder-text-secondary"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-4 top-1/2 transform -translate-y-1/2 w-6 h-6 flex items-center justify-center text-text-secondary hover:text-text-primary hover:bg-accent-light rounded-full transition-all duration-300"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
          )}

          {/* Chat Count */}
          <div className="mb-6">
            <p className="text-text-secondary text-lg">
              You have <span className="font-bold text-text-primary">{filteredConversations.length}</span> {title.toLowerCase().includes('dream') ? 'Dream Trips' : 'previous Places You\'ve Been'} with TravelStyle AI
              {searchQuery && (
                <span className="ml-1">
                  matching "<span className="font-semibold text-text-primary">{searchQuery}</span>"
                </span>
              )}
            </p>
          </div>
        </div>
      </div>

      {/* Chat List */}
      <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-secondary scrollbar-track-accent-light">
        <div className="max-w-4xl mx-auto p-4 lg:p-6">
        {filteredConversations.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-20 h-20 bg-gradient-to-br from-accent-light to-primary-light rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-sm">
              {title.toLowerCase().includes('favorite') ? (
                <Star className="w-10 h-10 text-text-secondary" />
              ) : (
                <Search className="w-10 h-10 text-text-secondary" />
              )}
            </div>
            <h3 className="text-2xl font-bold text-text-primary mb-3">
              {searchQuery 
                ? 'No chats found' 
                : title.toLowerCase().includes('favorite') 
                  ? 'No favorite chats yet' 
                  : 'No chats found'
              }
            </h3>
            <p className="text-text-secondary text-lg mb-8 max-w-md mx-auto leading-relaxed">
              {searchQuery 
                ? `No conversations match "${searchQuery}". Try different keywords or browse all your chats.`
                : title.toLowerCase().includes('favorite') 
                  ? 'Mark conversations as favorites by starring them. Your most important travel chats will appear here for quick access.' 
                  : 'Your conversation history will appear here once you start chatting. Begin your first travel planning session!'
              }
            </p>
            <button
              onClick={onNewChat}
              className="bg-gradient-to-r from-primary to-secondary text-background px-8 py-4 rounded-xl hover:from-secondary hover:to-primary transition-all duration-300 font-semibold shadow-lg hover:shadow-xl transform hover:scale-105"
            >
              {searchQuery ? 'Start New Chat' : 'Begin Your Journey'}
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            {sortedDateKeys.map((dateKey) => (
              <div key={dateKey}>
                {/* Date Header */}
                <h3 className="text-xl font-bold text-text-primary mt-8 mb-6 leading-tight">
                  {getDisplayGroupHeader(new Date(dateKey))}
                </h3>
                
                {/* Conversations for this date */}
                <div className="space-y-4">
                  {groupedConversations[dateKey].map((conversation) => (
                    <button
                      key={conversation.id}
                      onClick={() => onSelectChat(conversation.id)}
                      className="w-full text-left p-4 bg-surface hover:bg-background transition-all duration-300 rounded-2xl group shadow-md hover:shadow-xl border border-border hover:border-accent transform hover:scale-[1.02]"
                    >
                      <div className="flex items-start space-x-4 relative">
                        {/* Icon */}
                        <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-accent-light to-primary-light flex items-center justify-center flex-shrink-0 text-xl shadow-sm">
                          {conversation.icon || '💬'}
                        </div>
                        
                        {/* Content */}
                        <div className="flex-1 min-w-0">
                          <h4 className="text-lg font-bold text-text-primary mb-2 truncate leading-tight">
                            {conversation.title}
                          </h4>
                          <p className="text-text-secondary mb-1 line-clamp-2 text-base leading-relaxed">
                            {conversation.lastMessage}
                          </p>
                          
                          {/* Bottom row with message count, tags, and favorite */}
                          <div className="flex items-center space-x-3 mt-2">
                            {/* Message count */}
                            {conversation.messageCount && (
                              <div className="flex items-center space-x-2 text-text-secondary">
                                <MessageSquare className="w-4 h-4 text-text-secondary opacity-75" />
                                <span className="text-sm font-medium">{conversation.messageCount} messages</span>
                              </div>
                            )}
                            
                            {/* Time ago */}
                            <span className="text-sm text-text-secondary font-medium">
                              {formatTimeAgo(conversation.timestamp)}
                            </span>
                            
                            {/* Tags */}
                            {conversation.tags && conversation.tags.length > 0 && (
                              <div className="flex items-center space-x-2">
                                {conversation.tags.map((tag, tagIndex) => {
                                  const tagColor = getTagColor(tag);
                                  return (
                                    <span
                                      key={tagIndex}
                                      className={`px-3 py-1 rounded-full text-xs font-semibold ${tagColor.bg} ${tagColor.text} shadow-sm`}
                                    >
                                      {tag}
                                    </span>
                                  );
                                })}
                              </div>
                            )}
                            
                            {/* Favorite indicator */}
                            {conversation.isFavorite && (
                              <Star className="w-5 h-5 text-warning fill-current drop-shadow-sm" />
                            )}
                          </div>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
        </div>
      </div>
    </div>
  );
};

export default ChatHistoryPage;