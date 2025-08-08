import React, { useState, useCallback, useEffect } from 'react';
import LoginScreen from './components/LoginScreen';
import ForgotPasswordScreen from './components/ForgotPasswordScreen';
import ResetPasswordScreen from './components/ResetPasswordScreen';
import ProfilePage from './components/ProfilePage';
import ProfileSettingsMenu from './components/ProfileSettingsMenu';
import PersonalInformationForm from './components/PersonalInformationForm';
import StylePreferencesForm from './components/StylePreferencesForm';
import TravelPatternsForm from './components/TravelPatternsForm';
import PackingMethodsForm from './components/PackingMethodsForm';
import CurrencyPreferencesForm from './components/CurrencyPreferencesForm';
import SizeInformationForm from './components/SizeInformationForm';
import ChatHistoryPage from './components/ChatHistoryPage';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import { Menu, Sun, Moon } from 'lucide-react';
import { useAuth } from './hooks/useAuth';
import { ChatMessage, Conversation } from './types';

function App() {
  const { isAuthenticated, user, isLoading, login, logout, sendPasswordResetEmail, resetPassword } = useAuth();
  const [currentAuthView, setCurrentAuthView] = useState<'login' | 'forgotPassword' | 'resetPassword'>('login');
  const [resetToken, setResetToken] = useState<string>('');
  const [currentView, setCurrentView] = useState<'chat' | 'profile' | 'history'>('chat');
  const [profileSubView, setProfileSubView] = useState<'main' | 'settings' | 'personalForm' | 'styleForm' | 'travelForm' | 'packingForm' | 'currencyForm' | 'sizesForm'>('main');
  const [chatHistoryMode, setChatHistoryMode] = useState<'all' | 'favorites'>('all');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [selectedConversationId, setSelectedConversationId] = useState<string>();
  const [isDarkMode, setIsDarkMode] = useState(false);

  // Session-persistent greeting - generated once per session
  const [sessionGreeting] = useState(() => {
    const greetings = [
      "Hello",
      "Welcome back", 
      "Ready for your next adventure",
      "Let's explore the world together",
      "Your travel companion is here",
      "Time to discover something amazing",
      "Adventure awaits",
      "Let's plan your perfect trip",
      "Ready to explore",
      "Your journey starts here",
      "Let's make travel magic happen",
      "Welcome to your travel hub",
      "Ready for wanderlust",
      "Let's create unforgettable memories",
      "Your next adventure begins now"
    ];
    return greetings[Math.floor(Math.random() * greetings.length)];
  });

  // Check for password reset token in URL on component mount
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const type = urlParams.get('type');
    const accessToken = urlParams.get('access_token');
    
    if (type === 'recovery' && accessToken) {
      setResetToken(accessToken);
      setCurrentAuthView('resetPassword');
      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, []);

  // Theme toggle function
  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
    if (!isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  // Mock data
  const [conversations] = useState<Conversation[]>([
    {
      id: '1',
      title: 'Paris Fashion Week Trip',
      lastMessage: 'What should I pack for chilly weather?',
      timestamp: new Date(Date.now() - 7200000), // 2 hours ago
      unread: true,
      isFavorite: true,
      messageCount: 12,
      tags: ['wardrobe'],
      icon: '👗'
    },
    {
      id: '2',
      title: 'Business Trip to Tokyo',
      lastMessage: 'Professional outfits for meetings',
      timestamp: new Date(Date.now() - 86400000), // Yesterday
      isFavorite: false,
      messageCount: 8,
      tags: ['style'],
      icon: '🌏'
    },
    {
      id: '3',
      title: 'Mediterranean Cruise',
      lastMessage: 'Elegant evening wear suggestions',
      timestamp: new Date(Date.now() - 172800000), // 2 days ago
      isFavorite: true,
      messageCount: 15,
      tags: ['wardrobe', 'formal'],
      icon: '🚢'
    },
    {
      id: '4',
      title: 'Ski Trip to Alps',
      lastMessage: 'Stylish winter sports gear',
      timestamp: new Date(Date.now() - 259200000), // 3 days ago
      isFavorite: false,
      messageCount: 6,
      tags: ['winter', 'sports'],
      icon: '⛷️'
    },
    {
      id: '5',
      title: 'Summer Beach Vacation Wardrobe',
      lastMessage: 'Light fabrics and sun protection',
      timestamp: new Date(Date.now() - 432000000), // 5 days ago
      isFavorite: true,
      messageCount: 22,
      tags: ['summer', 'beach'],
      icon: '🏖️'
    },
    {
      id: '6',
      title: 'European Backpacking Adventure',
      lastMessage: 'Versatile pieces for multiple climates',
      timestamp: new Date(Date.now() - 1209600000), // 2 weeks ago
      isFavorite: false,
      messageCount: 18,
      tags: ['travel', 'versatile'],
      icon: '🎒'
    }
  ]);

  const handleSendMessage = useCallback((content: string) => {
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: generateAIResponse(content),
        sender: 'ai',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, aiMessage]);
      setIsTyping(false);
    }, 1500 + Math.random() * 1000);
  }, []);

  const generateAIResponse = (userMessage: string): string => {
    const responses = [
      "That's a great question! For your travel style needs, I'd recommend focusing on versatile pieces that can be mixed and matched. Consider packing items in a cohesive color palette - neutrals like navy, beige, and white work wonderfully for travel.",
      
      "Perfect timing to plan your wardrobe! Based on your destination, I suggest prioritizing comfort and style. Layering is key - pack lightweight cardigans or blazers that can elevate any outfit while keeping you comfortable during temperature changes.",
      
      "I love helping with travel style! For this type of trip, you'll want to balance practicality with sophistication. Consider wrinkle-resistant fabrics like ponte knits, jersey, and technical blends that maintain their shape throughout your journey.",
      
      "Excellent choice for your travel wardrobe! I recommend the capsule wardrobe approach - select 15-20 pieces that all coordinate with each other. This way, you can create multiple outfits while keeping your luggage light and organized.",
      
      "Great question about travel styling! Don't forget to consider your activities and the local dress code. Research your destination's style preferences and pack accordingly. Comfort should never be sacrificed for style when traveling."
    ];
    
    return responses[Math.floor(Math.random() * responses.length)];
  };

  const handleViewChatHistory = () => {
    setChatHistoryMode('all');
    setCurrentView('history');
  };

  const handleViewFavorites = () => {
    setChatHistoryMode('favorites');
    setCurrentView('history');
  };

  const handleNewChat = () => {
    setMessages([]);
    setSelectedConversationId(undefined);
    setCurrentView('chat');
  };

  const handleSelectChat = (id: string) => {
    setSelectedConversationId(id);
    setCurrentView('chat');
    // In a real app, you would load the conversation messages here
  };

  const handleConversationSelect = (id: string) => {
    setSelectedConversationId(id);
    setSidebarOpen(false);
    // In a real app, you would load the conversation messages here
  };

  const handleUpdateProfile = (updates: Partial<typeof user>) => {
    // In a real app, you would update the user profile in the backend
    console.log('Profile updates:', updates);
    // For demo purposes, we'll just log the updates
    // In a real implementation, this would update the user state
  };

  const handleProfileMenuItemClick = (action: string) => {
    switch (action) {
      case 'savedPlaces':
        handleViewFavorites();
        break;
      case 'billing':
        console.log('Navigate to billing page');
        break;
      case 'notifications':
        console.log('Navigate to notifications settings');
        break;
      case 'privacySecurity':
        console.log('Navigate to privacy & security settings');
        break;
      case 'travelAchievements':
        console.log('Navigate to travel achievements page');
        break;
      case 'helpSupport':
        console.log('Navigate to help & support page');
        break;
      default:
        console.log('Unknown menu item:', action);
    }
  };

  // Show login screen if not authenticated
  if (!isAuthenticated) {
    if (currentAuthView === 'forgotPassword') {
      return (
        <ForgotPasswordScreen
          onSendPasswordResetEmail={sendPasswordResetEmail}
          onBackToLogin={() => setCurrentAuthView('login')}
          isLoading={isLoading}
        />
      );
    }
    
    if (currentAuthView === 'resetPassword') {
      return (
        <ResetPasswordScreen
          onResetPassword={resetPassword}
          onBackToLogin={() => setCurrentAuthView('login')}
          accessToken={resetToken}
          isLoading={isLoading}
        />
      );
    }
    
    return (
      <LoginScreen 
        onLogin={login} 
        onForgotPassword={() => setCurrentAuthView('forgotPassword')}
        isLoading={isLoading} 
      />
    );
  }

  // Show profile page if user is viewing profile
  if (currentView === 'profile') {
    if (profileSubView === 'main') {
      return (
        <ProfilePage
          user={user!}
          onBack={() => setCurrentView('chat')}
          onEditProfileClick={() => setProfileSubView('settings')}
          onLogout={logout}
          onMenuItemClick={handleProfileMenuItemClick}
        />
      );
    } else if (profileSubView === 'settings') {
      return (
        <ProfileSettingsMenu
          onBack={() => setProfileSubView('main')}
          onSelectSetting={(setting) => {
            switch (setting) {
              case 'personal':
                setProfileSubView('personalForm');
                break;
              case 'style':
                setProfileSubView('styleForm');
                break;
              case 'travel':
                setProfileSubView('travelForm');
                break;
              case 'packing':
                setProfileSubView('packingForm');
                break;
              case 'currency':
                setProfileSubView('currencyForm');
                break;
              case 'sizes':
                setProfileSubView('sizesForm');
                break;
              default:
                // For unimplemented settings, just go back to settings menu
                break;
            }
          }}
        />
      );
    } else if (profileSubView === 'personalForm') {
      return (
        <PersonalInformationForm
          user={user!}
          onUpdateProfile={handleUpdateProfile}
          onBack={() => setProfileSubView('settings')}
        />
      );
    } else if (profileSubView === 'styleForm') {
      return (
        <StylePreferencesForm
          user={user!}
          onUpdateProfile={handleUpdateProfile}
          onBack={() => setProfileSubView('settings')}
        />
      );
    } else if (profileSubView === 'travelForm') {
      return (
        <TravelPatternsForm
          user={user!}
          onUpdateProfile={handleUpdateProfile}
          onBack={() => setProfileSubView('settings')}
        />
      );
    } else if (profileSubView === 'packingForm') {
      return (
        <PackingMethodsForm
          user={user!}
          onUpdateProfile={handleUpdateProfile}
          onBack={() => setProfileSubView('settings')}
        />
      );
    } else if (profileSubView === 'currencyForm') {
      return (
        <CurrencyPreferencesForm
          user={user!}
          onUpdateProfile={handleUpdateProfile}
          onBack={() => setProfileSubView('settings')}
        />
      );
    } else if (profileSubView === 'sizesForm') {
      return (
        <SizeInformationForm
          user={user!}
          onUpdateProfile={handleUpdateProfile}
          onBack={() => setProfileSubView('settings')}
        />
      );
    }
  }

  // Show chat history page
  if (currentView === 'history') {
    const filteredConversations = chatHistoryMode === 'favorites' 
      ? conversations.filter(conv => conv.isFavorite)
      : conversations;

    const historyTitle = chatHistoryMode === 'favorites' 
      ? 'Dream Trips' 
      : 'Places You\'ve Been';

    return (
      <ChatHistoryPage
        title={historyTitle}
        conversations={filteredConversations}
        onSelectChat={handleSelectChat}
        onNewChat={handleNewChat}
        onBack={() => setCurrentView('chat')}
      />
    );
  }

  // Show main app if authenticated
  return (
    <div className="flex flex-col h-screen bg-background">
      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          isOpen={sidebarOpen}
          onToggle={() => setSidebarOpen(!sidebarOpen)}
          conversations={conversations}
          onConversationSelect={handleConversationSelect}
          onViewChatHistory={handleViewChatHistory}
          onViewFavorites={handleViewFavorites}
          onNewChat={handleNewChat}
          selectedConversationId={selectedConversationId}
          user={user!}
          onProfileClick={() => {
            setCurrentView('profile');
            setProfileSubView('main');
          }}
          onLogout={logout}
          onToggleTheme={toggleTheme}
          isDarkMode={isDarkMode}
        />
        
        <div className="flex flex-col flex-1 min-w-0">
          <div className="flex-1 flex min-h-0 relative">
            {/* Floating Sidebar Toggle Button */}
            <div className="absolute top-4 left-4 z-20">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="w-10 h-10 flex items-center justify-center rounded-full bg-surface shadow-md hover:bg-accent-light transition-colors duration-300"
              >
                <Menu className="w-5 h-5 text-text-secondary" />
              </button>
            </div>
            
            {/* Floating Theme Toggle Button */}
            <div className="absolute top-4 right-4 z-20">
              <button
                onClick={toggleTheme}
                className="w-10 h-10 flex items-center justify-center rounded-full bg-surface shadow-md hover:bg-accent-light transition-colors duration-300"
              >
                {isDarkMode ? (
                  <Sun className="w-5 h-5 text-warning" />
                ) : (
                  <Moon className="w-5 h-5 text-text-secondary" />
                )}
              </button>
            </div>
            
            <ChatArea
              messages={messages}
              onSendMessage={handleSendMessage}
              isTyping={isTyping}
              user={user!}
              sessionGreeting={sessionGreeting}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;