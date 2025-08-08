import React from 'react';
import { Zap, Menu } from 'lucide-react';
import UserMenu from './UserMenu';
import { User as UserType } from '../types';

interface HeaderProps {
  user: UserType;
  onLogout: () => void;
  onProfileClick: () => void;
  onToggleSidebar: () => void;
}

const Header: React.FC<HeaderProps> = ({ user, onLogout, onProfileClick, onToggleSidebar }) => {
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-6">
      <div className="flex items-center justify-between mb-6">
        {/* Left side with toggle and title */}
        <div className="flex items-center space-x-4">
          <button
            onClick={onToggleSidebar}
            className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-gray-100 transition-colors duration-200"
          >
            <Menu className="w-5 h-5 text-gray-600" />
          </button>
        </div>
        
        {/* Right side with premium button and user menu */}
        <div className="flex items-center space-x-4">
          <button className="bg-gray-900 text-white px-4 py-2 rounded-full flex items-center space-x-2 hover:bg-gray-800 transition-colors duration-200">
            <Zap className="w-4 h-4" />
            <span className="font-medium">Try Premium</span>
          </button>
          
          <UserMenu user={user} onLogout={onLogout} onProfileClick={onProfileClick} />
        </div>
      </div>

      {/* Greeting and subtitle */}
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          {getGreeting()}, {user.name}!
        </h2>
        <p className="text-gray-600 text-lg">
          What can I assist you with today? Let's make things easier for you!
        </p>
      </div>

      {/* Quick info cards */}
      <div className="flex items-center space-x-8 text-sm">
        <div className="flex items-center space-x-2 text-blue-600">
          <div className="w-5 h-5 rounded-full bg-blue-100 flex items-center justify-center">
            <span className="text-xs">☀️</span>
          </div>
          <span className="font-medium">23°C Sunny</span>
        </div>
        
        <div className="flex items-center space-x-2 text-green-600">
          <div className="w-5 h-5 rounded-full bg-green-100 flex items-center justify-center">
            <span className="text-xs">$</span>
          </div>
          <span className="font-medium">1 USD = 0.85 EUR</span>
        </div>
        
        <div className="flex items-center space-x-2 text-red-600">
          <div className="w-5 h-5 rounded-full bg-red-100 flex items-center justify-center">
            <span className="text-xs">📍</span>
          </div>
          <span className="font-medium">San Francisco</span>
        </div>
      </div>
    </header>
  );
};

export default Header;