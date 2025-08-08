import React, { useState } from 'react';
import { ArrowLeft, Upload, User } from 'lucide-react';
import { User as UserType } from '../types';

interface PersonalInformationFormProps {
  user: UserType;
  onUpdateProfile: (updates: Partial<UserType>) => void;
  onBack: () => void;
}

const PersonalInformationForm: React.FC<PersonalInformationFormProps> = ({
  user,
  onUpdateProfile,
  onBack
}) => {
  const [firstName, setFirstName] = useState(user.firstName || '');
  const [lastName, setLastName] = useState(user.lastName || '');
  const [email, setEmail] = useState(user.email || '');
  const [defaultWeatherLocation, setDefaultWeatherLocation] = useState(user.defaultWeatherLocation || '');

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const handleSaveChanges = () => {
    onUpdateProfile({
      firstName,
      lastName,
      name: `${firstName} ${lastName}`,
      email,
      defaultWeatherLocation
    });
    onBack();
  };

  const handleCancel = () => {
    setFirstName(user.firstName || '');
    setLastName(user.lastName || '');
    setEmail(user.email || '');
    setDefaultWeatherLocation(user.defaultWeatherLocation || '');
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
            <h1 className="ml-4 text-2xl font-bold text-text-primary">Personal Information</h1>
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
        <div className="max-w-2xl mx-auto">
          {/* Profile Picture Section */}
          <div className="text-center mb-12">
            <div className="w-32 h-32 bg-gradient-to-br from-primary to-secondary rounded-full flex items-center justify-center mx-auto mb-6 shadow-2xl">
              {user.avatar ? (
                <img src={user.avatar} alt={user.name} className="w-32 h-32 rounded-full object-cover" />
              ) : (
                <span className="text-background text-3xl font-bold">
                  {getInitials(user.name)}
                </span>
              )}
            </div>
            <button className="inline-flex items-center space-x-2 px-6 py-3 border border-border text-text-secondary rounded-xl hover:bg-accent-light transition-all duration-300 font-medium">
              <Upload className="w-5 h-5" />
              <span>Change Picture</span>
            </button>
          </div>

          {/* Form Fields */}
          <div className="space-y-8">
            {/* Name Fields */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-text-primary mb-3">
                  First Name
                </label>
                <input
                  type="text"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  className="w-full px-4 py-4 border border-border bg-surface text-text-primary rounded-xl focus:ring-2 focus:ring-secondary focus:border-transparent transition-all duration-300 text-lg"
                  placeholder="Jane"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-primary mb-3">
                  Last Name
                </label>
                <input
                  type="text"
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  className="w-full px-4 py-4 border border-border bg-surface text-text-primary rounded-xl focus:ring-2 focus:ring-secondary focus:border-transparent transition-all duration-300 text-lg"
                  placeholder="Doe"
                />
              </div>
            </div>

            {/* Email Field */}
            <div>
              <label className="block text-sm font-medium text-text-primary mb-3">
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-4 border border-border bg-surface text-text-primary rounded-xl focus:ring-2 focus:ring-secondary focus:border-transparent transition-all duration-300 text-lg"
                placeholder="blbickham+100@gmail.com"
              />
            </div>

            {/* Default Weather Location */}
            <div>
              <label className="block text-sm font-medium text-text-primary mb-3">
                Default Weather Location
              </label>
              <input
                type="text"
                value={defaultWeatherLocation}
                onChange={(e) => setDefaultWeatherLocation(e.target.value)}
                className="w-full px-4 py-4 border border-border bg-surface text-text-primary rounded-xl focus:ring-2 focus:ring-secondary focus:border-transparent transition-all duration-300 text-lg"
                placeholder="Los Angeles, CA"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PersonalInformationForm;