import React, { useState } from 'react';
import { FilterOptions } from './interfaces';

interface SearchFiltersProps {
  filters: FilterOptions;
  onSearch: (params: {
    property_type: string;
    bhk: number | null;
    budget_cr: number | null;
    location: string;
    status: string;
    mode: 'STRICT' | 'FLEXIBLE';
  }) => void;
  loading: boolean;
}

export default function SearchFilters({ filters, onSearch, loading }: SearchFiltersProps) {
  const [propertyType, setPropertyType] = useState('');
  const [bhk, setBhk] = useState('');
  const [budget, setBudget] = useState('');
  const [location, setLocation] = useState('');
  const [status, setStatus] = useState('');
  const [mode, setMode] = useState<'STRICT' | 'FLEXIBLE'>('STRICT');

  const [locationSearch, setLocationSearch] = useState('');
  const [showLocationDropdown, setShowLocationDropdown] = useState(false);

  const filteredLocations = filters.locations.filter(loc =>
    loc.toLowerCase().includes(locationSearch.toLowerCase())
  );

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Parse BHK
    let bhkNum: number | null = null;
    if (bhk) {
      const match = bhk.match(/\d+/);
      if (match) {
        bhkNum = parseInt(match[0], 10);
      }
    }

    // Parse Budget
    const budgetNum = budget ? parseFloat(budget) : null;

    onSearch({
      property_type: propertyType,
      bhk: bhkNum,
      budget_cr: budgetNum,
      location: location,
      status: status,
      mode: mode,
    });
  };

  return (
    <form onSubmit={handleSearchSubmit} className="bg-white rounded-xl shadow-lg border border-gray-100 p-6 space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        
        {/* 1. Property Type Dropdown */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Property Type</label>
          <select
            value={propertyType}
            onChange={(e) => setPropertyType(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2.5 bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
          >
            <option value="">All Types</option>
            {filters.property_types.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </div>

        {/* 2. BHK Dropdown */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">BHK</label>
          <select
            value={bhk}
            onChange={(e) => setBhk(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2.5 bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
          >
            <option value="">All BHKs</option>
            {filters.bhks.map((b) => (
              <option key={b} value={b}>
                {b}
              </option>
            ))}
          </select>
        </div>

        {/* 3. Budget Input */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Max Budget (Cr)</label>
          <input
            type="number"
            step="0.01"
            min="0"
            placeholder="e.g. 1.20"
            value={budget}
            onChange={(e) => setBudget(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
          />
        </div>

        {/* 4. Searchable Location Auto-complete Dropdown */}
        <div className="relative">
          <label className="block text-sm font-medium text-gray-700 mb-2">Location</label>
          <input
            type="text"
            placeholder="Search Location..."
            value={locationSearch}
            onFocus={() => setShowLocationDropdown(true)}
            onChange={(e) => {
              setLocationSearch(e.target.value);
              // Clear actual set location if they start typing something else
              if (location !== e.target.value) {
                setLocation('');
              }
            }}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
          />
          {showLocationDropdown && (
            <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">
              <div 
                className="px-3 py-2 cursor-pointer hover:bg-gray-100 text-gray-500 text-sm"
                onClick={() => {
                  setLocation('');
                  setLocationSearch('');
                  setShowLocationDropdown(false);
                }}
              >
                Clear / All Locations
              </div>
              {filteredLocations.map((loc) => (
                <div
                  key={loc}
                  onClick={() => {
                    setLocation(loc);
                    setLocationSearch(loc);
                    setShowLocationDropdown(false);
                  }}
                  className="px-3 py-2 cursor-pointer hover:bg-blue-50 hover:text-blue-700 text-gray-900 text-sm transition"
                >
                  {loc}
                </div>
              ))}
              {filteredLocations.length === 0 && (
                <div className="px-3 py-2 text-gray-500 text-sm">No locations found</div>
              )}
            </div>
          )}
          {location && (
            <span className="absolute right-3 top-[38px] text-xs font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
              Selected
            </span>
          )}
        </div>

        {/* 5. Status Dropdown */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2.5 bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
          >
            <option value="">All Statuses</option>
            {filters.statuses.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>

        {/* Search Mode Toggle */}
        <div className="flex flex-col justify-end">
          <label className="block text-sm font-medium text-gray-700 mb-2">Search Mode</label>
          <div className="flex space-x-1 p-1 bg-gray-100 rounded-lg">
            <button
              type="button"
              onClick={() => setMode('STRICT')}
              className={`flex-1 text-center py-2 text-sm font-medium rounded-md transition ${
                mode === 'STRICT'
                  ? 'bg-white text-blue-700 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Strict Match (5/5)
            </button>
            <button
              type="button"
              onClick={() => setMode('FLEXIBLE')}
              className={`flex-1 text-center py-2 text-sm font-medium rounded-md transition ${
                mode === 'FLEXIBLE'
                  ? 'bg-white text-blue-700 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Flexible Match (3/5+)
            </button>
          </div>
        </div>
      </div>

      <div className="flex justify-end pt-4 border-t border-gray-100">
        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-semibold px-8 py-3 rounded-lg shadow transition flex items-center justify-center space-x-2"
        >
          {loading ? (
            <>
              <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              <span>Searching...</span>
            </>
          ) : (
            <span>FIND PROPERTIES</span>
          )}
        </button>
      </div>
    </form>
  );
}
