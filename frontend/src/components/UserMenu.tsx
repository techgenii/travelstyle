import React, { useState, useRef, useEffect } from 'react';
import { User, Settings, LogOut, CreditCard, Edit, Bell, Shield, Palette, Globe, Sun, Moon } from 'lucide-react';
import { User as UserType } from '../types';

interface UserMenuProps {
  user: UserType;
  onLogout: () => void;
  onProfileClick: () => void;
  onToggleTheme: () => void;
  isDarkMode: boolean;
  dropdownDirection?: 'top' | 'bottom';
  showFullLayout?: boolean;
}

const UserMenu: React.FC<UserMenuProps> = ({ 
  user, 
  onLogout, 
  onProfileClick, 
  onToggleTheme,
  isDarkMode,
  dropdownDirection = 'bottom',
  showFullLayout = false 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('profile');
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'settings', label: 'Settings', icon: Settings },
    { id: 'billing', label: 'Billing', icon: CreditCard }
  ];

  const renderProfileContent = () => (
    <div className="space-y-4">
      <div className="flex items-center space-x-3">
        <div className="w-12 h-12 bg-gradient-to-br from-primary to-secondary rounded-full flex items-center justify-center">
          {user.avatar ? (
            <img src={user.avatar} alt={user.name} className="w-12 h-12 rounded-full object-cover" />
          ) : (
            <span className="text-background text-lg font-semibold">
              {getInitials(user.name)}
            </span>
          )}
        </div>
        <div>
          <h3 className="font-semibold text-text-primary">{user.name}</h3>
          <p className="text-text-secondary text-sm">{user.email}</p>
          <p className="text-xs text-text-secondary opacity-75">Free Plan</p>
        </div>
      </div>
      
      <div className="border-t pt-4">
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm text-text-secondary">Member since</span>
            <span className="text-sm font-medium text-text-secondary">January 2025</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-text-secondary">Account status</span>
            <span className="text-sm font-medium text-success">Active</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-text-secondary">Travel chats</span>
            <span className="text-sm font-medium text-text-secondary">12</span>
          </div>
        </div>
      </div>
      
      <button 
        onClick={onProfileClick}
        className="w-full mt-4 bg-secondary-light text-secondary py-2 px-4 rounded-lg hover:bg-secondary hover:text-background transition-colors duration-300 flex items-center justify-center space-x-2"
      >
        <Edit size={16} />
        <span>View Profile</span>
      </button>
    </div>
  );

  const renderSettingsContent = () => (
    <div className="space-y-4">
      <div className="space-y-3">
        <div className="flex items-center justify-between py-2">
          <div className="flex items-center space-x-3">
            <Bell size={18} className="text-text-secondary" />
            <span className="text-sm text-text-secondary">Trip notifications</span>
          </div>
          <div className="relative">
            <input type="checkbox" className="sr-only" defaultChecked />
            <div className="w-10 h-6 bg-secondary rounded-full shadow-inner relative">
              <div className="w-4 h-4 bg-white rounded-full shadow absolute right-1 top-1"></div>
            </div>
          </div>
        </div>
        
        <div className="flex items-center justify-between py-2">
          <div className="flex items-center space-x-3">
            <Shield size={18} className="text-text-secondary" />
            <span className="text-sm text-text-secondary">Two-factor authentication</span>
          </div>
          <span className="text-xs bg-accent-light text-text-secondary px-2 py-1 rounded-full">Disabled</span>
        </div>
        
        <div className="flex items-center justify-between py-2">
          <div className="flex items-center space-x-3">
            {isDarkMode ? <Moon size={18} className="text-text-secondary" /> : <Sun size={18} className="text-text-secondary" />}
            <span className="text-sm text-text-secondary">Theme</span>
          </div>
          <button
            onClick={onToggleTheme}
            className="text-xs bg-secondary-light text-secondary px-3 py-1 rounded-full hover:bg-secondary hover:text-background transition-colors duration-300"
          >
            {isDarkMode ? 'Dark' : 'Light'}
          </button>
        </div>
        
        <div className="flex items-center justify-between py-2">
          <div className="flex items-center space-x-3">
            <Globe size={18} className="text-text-secondary" />
            <span className="text-sm text-text-secondary">Preferred currency</span>
          </div>
          <select className="text-sm border border-border bg-surface text-text-primary rounded px-2 py-1">
            <option>USD</option>
            <option>EUR</option>
            <option>GBP</option>
          </select>
        </div>
      </div>
      
      <div className="border-t pt-4">
        <h4 className="text-sm font-medium text-text-primary mb-3">Travel Preferences</h4>
        <div className="space-y-2">
          <label className="flex items-center space-x-2">
            <input type="checkbox" className="rounded" defaultChecked />
            <span className="text-sm text-text-secondary">Email travel recommendations</span>
          </label>
          <label className="flex items-center space-x-2">
            <input type="checkbox" className="rounded" defaultChecked />
            <span className="text-sm text-text-secondary">Share trip insights</span>
          </label>
        </div>
      </div>
    </div>
  );

  const renderBillingContent = () => (
    <div className="space-y-4">
      <div className="bg-gradient-to-r from-accent-light to-primary-light p-4 rounded-lg">
        <div className="flex justify-between items-start">
          <div>
            <h4 className="font-semibold text-text-primary">Free Plan</h4>
            <p className="text-sm text-text-secondary">$0/month</p>
          </div>
          <span className="bg-success-light text-success text-xs px-2 py-1 rounded-full">Active</span>
        </div>
        <p className="text-sm text-text-secondary mt-2">5 travel chats per month</p>
      </div>
      
      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-sm text-text-secondary">Usage this month</span>
          <span className="text-sm text-text-primary">3 / 5 chats</span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-sm text-text-secondary">Next reset</span>
          <span className="text-sm text-text-primary">February 28, 2025</span>
        </div>
        
        <div className="w-full bg-border rounded-full h-2">
          <div className="bg-secondary h-2 rounded-full" style={{ width: '60%' }}></div>
        </div>
      </div>
      
      <div className="border border-secondary bg-secondary-light p-4 rounded-lg">
        <h4 className="font-semibold text-secondary mb-2">Upgrade to Pro</h4>
        <p className="text-sm text-secondary mb-3">Unlimited travel planning and premium features</p>
        <button className="w-full bg-secondary text-background py-2 px-4 rounded-lg hover:bg-primary transition-colors duration-300">
          Upgrade for $9.99/month
        </button>
      </div>
      
      <div className="border-t pt-4 space-y-2">
        <button className="w-full text-left text-sm text-secondary hover:text-primary py-2 transition-colors duration-300">
          View billing history
        </button>
        <button className="w-full text-left text-sm text-secondary hover:text-primary py-2 transition-colors duration-300">
          Manage subscription
        </button>
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeTab) {
      case 'profile':
        return renderProfileContent();
      case 'settings':
        return renderSettingsContent();
      case 'billing':
        return renderBillingContent();
      default:
        return renderProfileContent();
    }
  };

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`${showFullLayout 
          ? 'w-full flex items-center space-x-3 p-3 rounded-lg hover:bg-accent-light transition-colors duration-300 cursor-pointer' 
          : 'p-1 rounded-lg hover:bg-accent-light transition-colors duration-300'
        }`}
      >
        {showFullLayout ? (
          <>
            <div className="w-8 h-8 bg-gradient-to-br from-primary to-secondary rounded-full flex items-center justify-center">
              {user.avatar ? (
                <img src={user.avatar} alt={user.name} className="w-8 h-8 rounded-full object-cover" />
              ) : (
                <span className="text-background text-sm font-semibold">
                  {getInitials(user.name)}
                </span>
              )}
            </div>
            <div className="flex-1 min-w-0 text-left">
              <p className="text-sm font-medium text-text-primary truncate">{user.name}</p>
              <div className="flex items-center space-x-1">
                <span className="text-xs text-text-secondary">Free Plan</span>
              </div>
            </div>
          </>
        ) : (
          <div className="w-8 h-8 bg-gradient-to-br from-primary to-secondary rounded-full flex items-center justify-center">
            {user.avatar ? (
              <img src={user.avatar} alt={user.name} className="w-8 h-8 rounded-full object-cover" />
            ) : (
              <span className="text-background text-sm font-semibold">
                {getInitials(user.name)}
              </span>
            )}
          </div>
        )}
      </button>

      {/* Enhanced Popup - positioned to the right and upward */}
      {isOpen && (
        <div className="absolute left-full bottom-0 ml-2 w-80 bg-surface rounded-xl shadow-xl border border-border z-50 transform transition-all duration-300">
          {/* Header with tabs */}
          <div className="border-b border-border">
            <div className="flex">
              {tabs.map((tab) => {
                const IconComponent = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex-1 px-4 py-3 text-sm font-medium transition-colors flex items-center justify-center space-x-2 ${
                      activeTab === tab.id
                        ? 'text-secondary border-b-2 border-secondary bg-secondary-light'
                        : 'text-text-secondary hover:text-text-primary hover:bg-accent-light'
                    }`}
                  >
                    <IconComponent size={16} />
                    <span className="hidden sm:inline">{tab.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Content */}
          <div className="p-6 max-h-96 overflow-y-auto">
            {renderContent()}
          </div>

          {/* Footer */}
          <div className="border-t border-border p-4">
            <button 
              onClick={onLogout}
              className="w-full flex items-center justify-center space-x-2 text-error hover:text-error text-sm py-2 hover:bg-error-light rounded-lg transition-colors duration-300"
            >
              <LogOut size={16} />
              <span>Sign out</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserMenu;