import React, { useState } from 'react';
import { 
  MessageSquarePlus,
  Search,
  Heart,
  Plane,
  X,
} from 'lucide-react';
import { Conversation } from '../types';
import { User as UserType } from '../types';
import UserMenu from './UserMenu';

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  conversations: Conversation[];
  onConversationSelect: (id: string) => void;
  onViewChatHistory: () => void;
  onViewFavorites: () => void;
  onNewChat: () => void;
  selectedConversationId?: string;
  user: UserType;
  onProfileClick: () => void;
  onLogout: () => void;
  onToggleTheme: () => void;
  isDarkMode: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  onToggle,
  conversations,
  onConversationSelect,
  onViewChatHistory,
  onViewFavorites,
  onNewChat,
  selectedConversationId,
  user,
  onProfileClick,
  onLogout,
  onToggleTheme,
  isDarkMode
}) => {
  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-text-primary bg-opacity-50 z-40 lg:hidden"
          onClick={onToggle}
        />
      )}
      
      {/* Mobile Sidebar */}
      <div className={`
        fixed left-0 top-0 h-full bg-surface z-50 transform transition-transform duration-300 ease-in-out lg:hidden
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        w-80
      `}>
        <div className="h-full flex flex-col">
          {/* Mobile Header with Close Button */}
          <div className="flex items-center justify-between p-4 border-b border-border">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-br from-primary to-secondary rounded-lg flex items-center justify-center">
                <Plane className="w-4 h-4 text-background" />
              </div>
              <span className="text-lg font-semibold text-text-primary">TravelStyle AI</span>
            </div>
            <button
              onClick={onToggle}
              className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-accent-light transition-colors duration-300"
            >
              <X className="w-5 h-5 text-text-secondary" />
            </button>
          </div>

          {/* Mobile Top Section */}
          <div className="p-3 border-b border-border">
            <button 
              onClick={onNewChat}
              className="w-full flex items-center space-x-3 p-3 rounded-lg hover:bg-accent-light transition-colors duration-300 text-left"
            >
              <MessageSquarePlus className="w-5 h-5 text-text-secondary" />
              <span className="text-text-primary font-medium">New chat</span>
            </button>
            
            <button 
              onClick={onViewChatHistory}
              className="w-full flex items-center space-x-3 p-3 rounded-lg hover:bg-accent-light transition-colors duration-300 text-left"
            >
              <Search className="w-5 h-5 text-text-secondary" />
              <span className="text-text-primary font-medium">Search chats</span>
            </button>
            
            <button 
              onClick={onViewFavorites}
              className="w-full flex items-center space-x-3 p-3 rounded-lg hover:bg-accent-light transition-colors duration-300 text-left"
            >
              <Heart className="w-5 h-5 text-text-secondary" />
              <span className="text-text-primary font-medium">Favorites</span>
            </button>
          </div>

          {/* Mobile Middle Section - Travel Chats */}
          <div className="flex-1 overflow-y-auto">
            <div className="p-3">
              <h3 className="text-sm font-medium text-text-secondary mb-3 px-3">Travel Chats</h3>
              <div className="space-y-1">
                {conversations.map((conversation) => (
                  <button
                    key={conversation.id}
                    onClick={() => {
                      onConversationSelect(conversation.id);
                      onToggle();
                    }}
                    className={`
                      w-full text-left p-3 rounded-lg transition-colors duration-200
                      ${selectedConversationId === conversation.id 
                        ? 'bg-accent-light' 
                        : 'hover:bg-primary-light'
                      }
                    `}
                  >
                    <p className="text-sm text-text-primary truncate font-medium">{conversation.title}</p>
                    <p className="text-xs text-text-secondary mt-1">{conversation.timestamp.toLocaleDateString()}</p>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Mobile Bottom Section */}
          <div className="border-t border-border p-3">
            <UserMenu 
              user={user} 
              onLogout={onLogout} 
              onProfileClick={onProfileClick}
              onToggleTheme={onToggleTheme}
              isDarkMode={isDarkMode}
              dropdownDirection="top"
              showFullLayout={true}
            />
          </div>
        </div>
      </div>

      {/* Desktop Sidebar */}
      <div className={`
        hidden lg:flex flex-col bg-surface border-r border-border transition-all duration-300 ease-in-out h-full
        ${isOpen ? 'w-80' : 'w-0'}
      `}>
        {/* Desktop Top Section - Fixed */}
        <div className="border-b border-border">
          {/* Logo */}
          <div className="p-3">
            <button 
              onClick={onToggle}
              className="flex items-center space-x-3 mb-4 w-full text-left hover:bg-accent-light rounded-lg p-2 -m-2 transition-colors duration-300"
            >
              <div className="w-8 h-8 bg-gradient-to-br from-primary to-secondary rounded-lg flex items-center justify-center">
                <Plane className="w-4 h-4 text-background" />
              </div>
              <span className="text-lg font-semibold text-text-primary">TravelStyle AI</span>
            </button>
          </div>

          {/* Top Menu Items */}
          <div className="px-3 pb-3">
            <button 
              onClick={onNewChat}
              className="w-full flex items-center space-x-3 p-3 rounded-lg hover:bg-accent-light transition-colors duration-300 text-left"
            >
              <MessageSquarePlus className="w-5 h-5 text-text-secondary" />
              <span className="text-text-primary font-medium">New chat</span>
            </button>
            
            <button 
              onClick={onViewChatHistory}
              className="w-full flex items-center space-x-3 p-3 rounded-lg hover:bg-accent-light transition-colors duration-300 text-left"
            >
              <Search className="w-5 h-5 text-text-secondary" />
              <span className="text-text-primary font-medium">Search chats</span>
            </button>
            
            <button 
              onClick={onViewFavorites}
              className="w-full flex items-center space-x-3 p-3 rounded-lg hover:bg-accent-light transition-colors duration-300 text-left"
            >
              <Heart className="w-5 h-5 text-text-secondary" />
              <span className="text-text-primary font-medium">Favorites</span>
            </button>
          </div>
        </div>

        {/* Desktop Middle Section - Scrollable Travel Chats */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-3">
            <h3 className="text-sm font-medium text-text-secondary mb-3 px-3">Travel Chats</h3>
            <div className="space-y-1">
              {conversations.map((conversation) => (
                <button
                  key={conversation.id}
                  onClick={() => onConversationSelect(conversation.id)}
                  className={`
                    w-full text-left p-3 rounded-lg transition-colors duration-200
                    ${selectedConversationId === conversation.id 
                      ? 'bg-accent-light' 
                      : 'hover:bg-primary-light'
                    }
                  `}
                >
                  <p className="text-sm text-text-primary truncate font-medium">{conversation.title}</p>
                  <p className="text-xs text-text-secondary mt-1">{conversation.timestamp.toLocaleDateString()}</p>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Desktop Bottom Section - Fixed */}
        <div className="border-t border-border">
          <div className="p-3 relative">
            <UserMenu 
              user={user} 
              onLogout={onLogout} 
              onProfileClick={onProfileClick}
              onToggleTheme={onToggleTheme}
              isDarkMode={isDarkMode}
              dropdownDirection="top"
              showFullLayout={true}
            />
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;