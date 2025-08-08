import React, { useState } from 'react';
import { 
  ArrowLeft,
  MapPin,
  Calendar,
  Shield,
  HelpCircle,
  Heart,
  Star,
  LogOut,
  ChevronRight,
  Globe,
  Plane,
  Camera,
  Award,
  TrendingUp,
  Edit,
  Save,
  X,
  CreditCard,
  Bell
} from 'lucide-react';
import { User as UserType } from '../types';

interface ProfilePageProps {
  user: UserType;
  onBack: () => void;
  onEditProfileClick: () => void;
  onLogout: () => void;
  onMenuItemClick: (action: string) => void;
}

const ProfilePage: React.FC<ProfilePageProps> = ({ user, onBack, onEditProfileClick, onLogout, onMenuItemClick }) => {

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const menuItems = [
    // Left column
    {
      id: 'billing',
      icon: CreditCard,
      title: 'Billing',
      subtitle: 'Manage your subscription and payment methods',
      color: 'text-primary',
      bgColor: 'bg-primary-light'
    },
    {
      id: 'savedPlaces',
      icon: Heart,
      title: 'Saved Places',
      subtitle: '12 dream destinations bookmarked',
      color: 'text-error',
      bgColor: 'bg-error-light'
    },
    {
      id: 'privacySecurity',
      icon: Shield,
      title: 'Privacy & Security',
      subtitle: 'Manage your data and security settings',
      color: 'text-success',
      bgColor: 'bg-success-light'
    },
    // Right column
    {
      id: 'travelAchievements',
      icon: Award,
      title: 'Travel Achievements',
      subtitle: 'Your journey milestones and badges',
      color: 'text-warning',
      bgColor: 'bg-warning-light'
    },
    {
      id: 'notifications',
      icon: Bell,
      title: 'Notifications',
      subtitle: 'Manage your travel alerts and updates',
      color: 'text-secondary',
      bgColor: 'bg-secondary-light'
    },
    {
      id: 'helpSupport',
      icon: HelpCircle,
      title: 'Help & Support',
      subtitle: 'FAQs, guides, and contact support',
      color: 'text-accent',
      bgColor: 'bg-accent-light'
    }
  ];

  return (
    <div className="flex flex-col min-h-screen bg-background">
      {/* Header */}
      <div className="bg-surface border-b border-border px-4 lg:px-8 py-6 shadow-sm">
        <div className="w-full flex items-center">
          <button
            onClick={onBack}
            className="w-12 h-12 flex items-center justify-center rounded-xl hover:bg-accent-light transition-all duration-300 shadow-sm hover:shadow-md"
          >
            <ArrowLeft className="w-6 h-6 text-text-secondary" />
          </button>
          <h1 className="ml-4 text-2xl font-bold text-text-primary">Profile</h1>
          <button
            onClick={onLogout}
            className="ml-auto w-12 h-12 flex items-center justify-center rounded-xl hover:bg-error-light transition-all duration-300 shadow-sm hover:shadow-md"
          >
            <LogOut className="w-6 h-6 text-error" />
          </button>
        </div>
      </div>

      <div className="flex-1 w-full px-4 sm:px-6 lg:px-8 py-8">
        {/* Profile Hero Section */}
        <div className="bg-surface rounded-3xl shadow-xl p-8 sm:p-12 mb-8 text-center relative overflow-hidden">
          {/* Background Pattern */}
          <div className="absolute inset-0 bg-gradient-to-br from-primary-light via-secondary-light to-accent-light opacity-30"></div>
          <div className="absolute inset-0 bg-gradient-to-t from-transparent via-transparent to-surface opacity-60"></div>
          
          {/* Content */}
          <div className="relative z-10 text-center">
            {/* Profile Picture */}
            <div className="w-32 h-32 bg-gradient-to-br from-primary to-secondary rounded-full flex items-center justify-center mx-auto mb-6 shadow-2xl">
              {user.avatar ? (
                <img src={user.avatar} alt={user.name} className="w-32 h-32 rounded-full object-cover" />
              ) : (
                <span className="text-background text-3xl font-bold">
                  {getInitials(user.name)}
                </span>
              )}
            </div>

            {/* User Info */}
            <h1 className="text-3xl font-bold text-text-primary mb-2">{user.name}</h1>
            <p className="text-lg text-text-secondary mb-6">{user.email}</p>
            <button
              onClick={onEditProfileClick}
              className="bg-transparent border border-secondary text-secondary px-6 py-3 rounded-full font-semibold hover:bg-secondary hover:text-background transition-colors duration-300"
            >
              Edit Travel Preferences
            </button>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Travel Statistics */}
          <div className="bg-surface rounded-3xl shadow-xl p-6 sm:p-8">
            <div className="flex items-center mb-8">
              <div className="w-12 h-12 bg-gradient-to-br from-primary to-secondary rounded-xl flex items-center justify-center mr-4 shadow-lg">
                <TrendingUp className="w-6 h-6 text-background" />
              </div>
              <h2 className="text-2xl font-bold text-text-primary">Travel Statistics</h2>
            </div>
            
            <div className="grid grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-5xl font-bold text-secondary mb-2">8</div>
                <div className="text-base text-text-secondary font-medium">Countries</div>
                <div className="text-sm text-text-secondary opacity-75">Visited</div>
              </div>
              <div className="text-center">
                <div className="text-5xl font-bold text-secondary mb-2">24</div>
                <div className="text-base text-text-secondary font-medium">Cities</div>
                <div className="text-sm text-text-secondary opacity-75">Explored</div>
              </div>
              <div className="text-center">
                <div className="text-5xl font-bold text-secondary mb-2">156</div>
                <div className="text-base text-text-secondary font-medium">Travel</div>
                <div className="text-sm text-text-secondary opacity-75">Days</div>
              </div>
            </div>
            
            <div className="border-t border-border pt-6 mt-8">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="flex justify-between items-center">
                  <span className="text-text-secondary">Member since</span>
                  <span className="font-semibold text-text-primary">January 2025</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-text-secondary">Account status</span>
                  <span className="font-semibold text-success">Active</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-text-secondary">Travel chats</span>
                  <span className="font-semibold text-text-primary">12</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-text-secondary">Favorites</span>
                  <span className="font-semibold text-text-primary">3</span>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Trip */}
          <div className="bg-surface rounded-3xl shadow-xl p-6 sm:p-8">
            <div className="flex items-center mb-8">
              <div className="w-12 h-12 bg-gradient-to-br from-accent to-primary rounded-xl flex items-center justify-center mr-4 shadow-lg">
                <Plane className="w-6 h-6 text-background" />
              </div>
              <h2 className="text-2xl font-bold text-text-primary">Recent Adventure</h2>
            </div>
            
            <div className="flex items-start space-x-6">
              <div className="w-24 h-24 rounded-2xl overflow-hidden flex-shrink-0 shadow-lg">
                <img 
                  src="https://images.pexels.com/photos/338515/pexels-photo-338515.jpeg?auto=compress&cs=tinysrgb&w=400" 
                  alt="Paris, France" 
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="flex-1">
                <h3 className="text-xl font-bold text-text-primary mb-2">Paris, France</h3>
                <div className="flex items-center text-text-secondary text-base mb-3">
                  <Calendar className="w-5 h-5 mr-2" />
                  <span>March 15-22, 2024</span>
                </div>
                <p className="text-text-secondary text-base leading-relaxed mb-4">
                  7 magical days exploring the City of Light, from the Eiffel Tower to charming Montmartre cafés.
                </p>
                <div className="flex items-center space-x-4">
                  <div className="flex items-center text-sm text-text-secondary">
                    <Camera className="w-4 h-4 mr-1" />
                    <span>47 photos</span>
                  </div>
                  <div className="flex items-center text-sm text-text-secondary">
                    <Heart className="w-4 h-4 mr-1" />
                    <span>5 favorites</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Menu Items Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {menuItems.map((item, index) => (
            <button
              key={index}
              onClick={() => onMenuItemClick(item.id)}
              className="bg-surface hover:bg-background transition-all duration-300 rounded-3xl p-6 shadow-xl hover:shadow-2xl border border-border hover:border-accent transform hover:scale-[1.02] text-left group"
            >
              <div className="flex items-start space-x-4">
                <div className={`w-14 h-14 ${item.bgColor} rounded-2xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-all duration-300`}>
                  <item.icon className={`w-7 h-7 ${item.color}`} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <h3 className="text-xl font-bold text-text-primary mb-2">{item.title}</h3>
                    <ChevronRight className="w-6 h-6 text-text-secondary group-hover:text-text-primary transition-colors duration-300" />
                  </div>
                  <p className="text-base text-text-secondary leading-relaxed">{item.subtitle}</p>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;