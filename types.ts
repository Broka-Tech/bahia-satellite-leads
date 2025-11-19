export interface Property {
  id: string;
  title: string;
  location: {
    city: string;
    neighborhood: string;
  };
  price: number;
  bedrooms: number;
  area: number;
  imageUrl: string;
  type: 'apartment' | 'house' | 'penthouse';
  isExclusive?: boolean;
  tags: string[];
  aiGeneratedTitle?: string; // Populated by Gemini
  priceHistory?: { date: string; price: number }[];
}

export interface FilterState {
  priceRange: [number, number];
  neighborhoods: string[];
  profile: 'all' | 'economic' | 'standard' | 'luxury' | 'ultra-luxury';
  bedrooms: number | null;
}

export interface LeadData {
  propertyId: string;
  customerName: string;
  customerPhone: string;
  intent: string;
}