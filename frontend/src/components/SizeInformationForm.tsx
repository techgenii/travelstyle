import React, { useState } from 'react';
import { ArrowLeft, Ruler } from 'lucide-react';
import { User as UserType } from '../types';

interface SizeInformationFormProps {
  user: UserType;
  onUpdateProfile: (updates: Partial<UserType>) => void;
  onBack: () => void;
}

const SizeInformationForm: React.FC<SizeInformationFormProps> = ({
  user,
  onUpdateProfile,
  onBack
}) => {
  const [shirtSize, setShirtSize] = useState(user.shirtSize || '');
  const [pantSize, setPantSize] = useState(user.pantSize || '');
  const [shoeSize, setShoeSize] = useState(user.shoeSize || '');
  const [dressSize, setDressSize] = useState(user.dressSize || '');
  const [skirtSize, setSkirtSize] = useState(user.skirtSize || '');
  const [bathingSuitSize, setBathingSuitSize] = useState(user.bathingSuitSize || '');

  const handleSaveChanges = () => {
    onUpdateProfile({
      shirtSize,
      pantSize,
      shoeSize,
      dressSize,
      skirtSize,
      bathingSuitSize
    });
    onBack();
  };

  const handleCancel = () => {
    setShirtSize(user.shirtSize || '');
    setPantSize(user.pantSize || '');
    setShoeSize(user.shoeSize || '');
    setDressSize(user.dressSize || '');
    setSkirtSize(user.skirtSize || '');
    setBathingSuitSize(user.bathingSuitSize || '');
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
                <Ruler className="w-6 h-6 text-primary" />
                <h1 className="text-2xl font-bold text-text-primary">Size Information</h1>
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
        <div className="max-w-2xl mx-auto">
          {/* Form Fields */}
          <div className="space-y-6">
            {/* Row 1: Shirt and Pant Size */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-semibold text-text-primary mb-3">
                  Shirt Size
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={shirtSize}
                    onChange={(e) => setShirtSize(e.target.value)}
                    className="w-full px-6 py-4 border-2 border-border bg-surface text-text-primary rounded-2xl focus:ring-4 focus:ring-secondary focus:ring-opacity-20 focus:border-secondary transition-all duration-300 text-lg shadow-sm hover:shadow-md hover:border-accent"
                    placeholder="XL"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-semibold text-text-primary mb-3">
                  Pant Size
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={pantSize}
                    onChange={(e) => setPantSize(e.target.value)}
                    className="w-full px-6 py-4 border-2 border-border bg-surface text-text-primary rounded-2xl focus:ring-4 focus:ring-secondary focus:ring-opacity-20 focus:border-secondary transition-all duration-300 text-lg shadow-sm hover:shadow-md hover:border-accent"
                    placeholder="16, XL"
                  />
                </div>
              </div>
            </div>

            {/* Row 2: Shoe and Dress Size */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-semibold text-text-primary mb-3">
                  Shoe Size
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={shoeSize}
                    onChange={(e) => setShoeSize(e.target.value)}
                    className="w-full px-6 py-4 border-2 border-border bg-surface text-text-primary rounded-2xl focus:ring-4 focus:ring-secondary focus:ring-opacity-20 focus:border-secondary transition-all duration-300 text-lg shadow-sm hover:shadow-md hover:border-accent"
                    placeholder="10.0"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-semibold text-text-primary mb-3">
                  Dress Size
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={dressSize}
                    onChange={(e) => setDressSize(e.target.value)}
                    className="w-full px-6 py-4 border-2 border-border bg-surface text-text-primary rounded-2xl focus:ring-4 focus:ring-secondary focus:ring-opacity-20 focus:border-secondary transition-all duration-300 text-lg shadow-sm hover:shadow-md hover:border-accent"
                    placeholder="16"
                  />
                </div>
              </div>
            </div>

            {/* Row 3: Skirt and Bathing Suit Size */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-semibold text-text-primary mb-3">
                  Skirt Size
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={skirtSize}
                    onChange={(e) => setSkirtSize(e.target.value)}
                    className="w-full px-6 py-4 border-2 border-border bg-surface text-text-primary rounded-2xl focus:ring-4 focus:ring-secondary focus:ring-opacity-20 focus:border-secondary transition-all duration-300 text-lg shadow-sm hover:shadow-md hover:border-accent"
                    placeholder="16"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-semibold text-text-primary mb-3">
                  Bathing Suit Size
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={bathingSuitSize}
                    onChange={(e) => setBathingSuitSize(e.target.value)}
                    className="w-full px-6 py-4 border-2 border-border bg-surface text-text-primary rounded-2xl focus:ring-4 focus:ring-secondary focus:ring-opacity-20 focus:border-secondary transition-all duration-300 text-lg shadow-sm hover:shadow-md hover:border-accent"
                    placeholder="XL"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SizeInformationForm;