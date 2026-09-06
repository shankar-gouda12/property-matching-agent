import React from 'react';
import { PropertyMatch } from './interfaces';
import PropertyCard from './PropertyCard';

interface PropertyResultsProps {
  matches: PropertyMatch[];
  searchPerformed: boolean;
  reqCriteria: {
    property_type?: string;
    bhk?: number | null;
    budget_cr?: number | null;
    location?: string;
    status?: string;
  } | null;
}

export default function PropertyResults({ matches, searchPerformed, reqCriteria }: PropertyResultsProps) {
  if (!searchPerformed) {
    return (
      <div className="bg-gray-50 border border-dashed border-gray-200 rounded-xl p-12 text-center">
        <svg className="w-12 h-12 text-gray-300 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <p className="text-gray-500 font-medium">Use the filters above to search your property inventory.</p>
      </div>
    );
  }

  if (matches.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow border border-red-100 p-8 text-center space-y-4">
        <div className="w-12 h-12 rounded-full bg-red-50 flex items-center justify-center mx-auto text-red-500 text-xl font-bold">
          !
        </div>
        <h3 className="text-lg font-bold text-gray-900">No exact properties found for the selected requirements.</h3>
        
        {reqCriteria && (
          <div className="inline-block bg-gray-50 border border-gray-200 rounded-lg p-4 text-left text-sm text-gray-600 max-w-md w-full">
            <span className="font-bold text-gray-800 block mb-1">Your requirements:</span>
            <ul className="list-disc pl-5 space-y-1">
              {reqCriteria.property_type && <li>Property Type: {reqCriteria.property_type}</li>}
              {reqCriteria.bhk && <li>BHK: {reqCriteria.bhk} BHK</li>}
              {reqCriteria.budget_cr && <li>Budget: ₹{reqCriteria.budget_cr} Cr</li>}
              {reqCriteria.location && <li>Location: {reqCriteria.location}</li>}
              {reqCriteria.status && <li>Status: {reqCriteria.status}</li>}
            </ul>
          </div>
        )}
        <p className="text-gray-500 text-sm">Try adjusting your budget or selecting a more flexible match mode.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900">
          {matches.length} {matches.length === 1 ? 'PROPERTY' : 'PROPERTIES'} FOUND
        </h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {matches.map((item, index) => (
          <PropertyCard key={index} property={item} />
        ))}
      </div>
    </div>
  );
}
