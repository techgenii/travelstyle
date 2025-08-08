import React, { useState } from 'react';
import { ArrowLeft, Check, Plane } from 'lucide-react';
import { User as UserType } from '../types';

interface TravelPatternsFormProps {
  user: UserType;
  onUpdateProfile: (updates: Partial<UserType>) => void;
  onBack: () => void;
}

const TravelPatternsForm: React.FC<TravelPatternsFormProps> = ({
  user,
  onUpdateProfile,
  onBack
}) => {
  const [selectedPatterns, setSelectedPatterns] = useState<string[]>(user.travelPatterns || []);

  const travelOptions = [
    'Business',
    'Leisure',
    'Adventure',
    'Family',
    'Solo',
    'Romantic',
    'Cultural',
    'Relaxation',
    'Road Trip',
    'Cruise'
  ];

  const togglePattern = (pattern: string) => {
    setSelectedPatterns(prev => 
      prev.includes(pattern) 
        ? prev.filter(p => p !== pattern)
        : [...prev, pattern]
    );
  };

  const handleSaveChanges = () => {
    onUpdateProfile({ travelPatterns: selectedPatterns });
    onBack();
  };

  const handleCancel = () => {
    setSelectedPatterns(user.travelPatterns || []);
    onBack();
  };

  return (
    <div className="flex flex-col min-h-screen bg-background">
      {/* Header */}
      <div className="bg-surface border-b border-border px-4 lg:px-8 py-6 shadow-sm">
        <div className="w-full flex items-center justify-between">
          <div className="flex items-center">
            <button
              onClick={onBack}
              className="w-12 h-12 flex items-center justify-center rounded-xl hover:bg-accent-light transition-all duration-300 shadow-sm hover:shadow-md"
            >
              <ArrowLeft className="w-6 h-6 text-text-secondary" />
            </button>
            <div className="ml-4">
              <div className="flex items-center space-x-3 mb-1">
                <Plane className="w-6 h-6 text-primary" />
                <h1 className="text-2xl font-bold text-text-primary">Travel Patterns</h1>
              </div>
            </div>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={handleCancel}
              className="px-6 py-3 border border-border text-text-secondary rounded-xl hover:bg-accent-light transition-all duration-300 font-medium"
            >
              Cancel
            </button>
            <button
              onClick={handleSaveChanges}
              className="px-6 py-3 bg-primary text-background rounded-xl hover:bg-secondary transition-all duration-300 font-medium shadow-lg hover:shadow-xl"
            >
              Save Changes
            </button>
          </div>
        </div>
      </div>

      {/* Form Content */}
      <div className="flex-1 w-full px-4 sm:px-6 lg:px-8 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-text-primary mb-2">Travel Types</h2>
            <p className="text-text-secondary">Select your common travel types:</p>
          </div>

          {/* Travel Options Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {travelOptions.map((pattern) => {
              const isSelected = selectedPatterns.includes(pattern);
              return (
                <button
                  key={pattern}
                  onClick={() => togglePattern(pattern)}
                  className={`
                    p-6 rounded-2xl border transition-all duration-300 text-left group relative
                    ${isSelected 
                      ? 'bg-primary-light border-primary text-primary shadow-lg' 
                      : 'bg-surface border-border text-text-primary hover:bg-accent-light hover:border-accent'
                    }
                  `}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-lg font-medium">{pattern}</span>
                    {isSelected && (
                      <div className="w-6 h-6 bg-primary rounded-full flex items-center justify-center">
                        <Check className="w-4 h-4 text-background" />
                      </div>
                    )}
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

export default TravelPatternsForm;