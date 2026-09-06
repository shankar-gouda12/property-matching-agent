export interface PropertyMatchDetails {
  property_type: boolean;
  bhk: boolean;
  budget: boolean;
  location: boolean;
  status: boolean;
}

export interface PropertyMatch {
  score: string;
  details: Record<string, any>;
  match_details: PropertyMatchDetails;
}

export interface SearchResponse {
  success: boolean;
  total_matches: number;
  matches: PropertyMatch[];
}

export interface FilterOptions {
  property_types: string[];
  bhks: string[];
  locations: string[];
  statuses: string[];
}
