export interface ChatMessage {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  isTyping?: boolean;
}

export interface Conversation {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: Date;
  unread?: boolean;
  isFavorite?: boolean;
  messageCount?: number;
  tags?: string[];
  icon?: string;
}

export interface User {
  id: string;
  name: string;
  firstName: string;
  lastName: string;
  email: string;
  avatar?: string;
  defaultWeatherLocation?: string;
  styles?: string[];
  travelPatterns?: string[];
  packingMethods?: string[];
  currencies?: string[];
  shirtSize?: string;
  pantSize?: string;
  shoeSize?: string;
  dressSize?: string;
  skirtSize?: string;
  bathingSuitSize?: string;
}

export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  isLoading: boolean;
}