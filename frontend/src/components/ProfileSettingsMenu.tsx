import React from 'react';
import { ArrowLeft, User, Palette, Package, DollarSign, Plane, Ruler, MessageSquareText } from 'lucide-react';

interface ProfileSettingsMenuProps {
  onBack: () => void;
  onSelectSetting: (setting: string) => void;
}

const ProfileSettingsMenu: React.FC<ProfileSettingsMenuProps> = ({
  onBack,
  onSelectSetting
}) => {
  const menuItems = [
    {
      id: 'personal',
      title: 'Personal',
      icon: User,
      isPrimary: true
    },
    {
      id: 'style',
      title: 'Style',
      icon: Palette,
      isPrimary: false
    },
    {
      id: 'packing',
      title: 'Packing',
      icon: Package,
      isPrimary: false
    },
    {
      id: 'currency',
      title: 'Currency',
      icon: DollarSign,
      isPrimary: false
    },
    {
      id: 'travel',
      title: 'Travel',
      icon: Plane,
      isPrimary: false
    },
    {
      id: 'sizes',
      title: 'Sizes',
      icon: Ruler,
      isPrimary: false
    },
    {
      id: 'quickReplies',
      title: 'Quick Replies',
      icon: MessageSquareText,
      isPrimary: false
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
          <h1 className="ml-4 text-2xl font-bold text-text-primary">Travel Preference Settings</h1>
        </div>
      </div>

      {/* Menu Grid */}
      <div className="flex-1 w-full px-4 sm:px-6 lg:px-8 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {menuItems.map((item) => {
              const IconComponent = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => onSelectSetting(item.id)}
                  className={`
                    p-6 rounded-2xl border transition-all duration-300 text-left group hover:shadow-lg transform hover:scale-[1.02]
                    ${item.isPrimary 
                      ? 'bg-primary text-background border-primary shadow-lg' 
                      : 'bg-surface text-text-primary border-border hover:bg-background hover:border-accent'
                    }
                  `}
                >
                  <div className="flex items-center space-x-4">
                    <div className={`
                      w-12 h-12 rounded-xl flex items-center justify-center transition-all duration-300
                      ${item.isPrimary 
                        ? 'bg-background bg-opacity-20' 
                        : 'bg-accent-light group-hover:bg-primary-light'
                      }
                    `}>
                      <IconComponent className={`
                        w-6 h-6 transition-colors duration-300
                        ${item.isPrimary 
                          ? 'text-background' 
                          : 'text-text-secondary group-hover:text-primary'
                        }
                      `} />
                    </div>
                    <div className="flex-1">
                      <h3 className={`
                        text-lg font-semibold transition-colors duration-300
                        ${item.isPrimary 
                          ? 'text-background' 
                          : 'text-text-primary'
                        }
                      `}>
                        {item.title}
                      </h3>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileSettingsMenu;