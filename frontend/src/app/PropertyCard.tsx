import React, { useState } from 'react';
import { PropertyMatch } from './interfaces';

interface PropertyCardProps {
  property: PropertyMatch;
}

export default function PropertyCard({ property }: PropertyCardProps) {
  const [showModal, setShowModal] = useState(false);
  const details = property.details;
  const matchDetails = property.match_details;

  // Format currency
  const formatBudget = (val: any) => {
    if (val === null || val === undefined) return 'N/A';
    return `₹${val} Cr`;
  };

  const getScoreColor = (score: string) => {
    if (score === '5/5') return 'bg-green-100 text-green-800 border-green-200';
    if (score.startsWith('4') || score.startsWith('3')) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    return 'bg-red-100 text-red-800 border-red-200';
  };

  return (
    <>
      <div className="bg-white rounded-xl shadow-md border border-gray-100 p-6 flex flex-col justify-between hover:shadow-lg transition">
        <div>
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-lg font-bold text-gray-900 leading-snug">
              {details["Project Name"] || details["Property Name"] || "Unnamed Project"}
            </h3>
            <span className={`px-2.5 py-1 text-xs font-semibold rounded-full border ${getScoreColor(property.score)}`}>
              MATCH: {property.score}
            </span>
          </div>

          <div className="space-y-2.5 text-sm text-gray-600 mb-6">
            {/* Property Type */}
            <div className="flex items-center justify-between">
              <span className="font-medium text-gray-500">Property Type:</span>
              <div className="flex items-center space-x-1.5">
                <span className="text-gray-950 font-semibold">{details["Property Type"] || 'N/A'}</span>
                <span>{matchDetails.property_type ? '✅' : '❌'}</span>
              </div>
            </div>

            {/* BHK */}
            <div className="flex items-center justify-between">
              <span className="font-medium text-gray-500">BHK:</span>
              <div className="flex items-center space-x-1.5">
                <span className="text-gray-950 font-semibold">{details["BHK"] || 'N/A'}</span>
                <span>{matchDetails.bhk ? '✅' : '❌'}</span>
              </div>
            </div>

            {/* Budget */}
            <div className="flex items-center justify-between">
              <span className="font-medium text-gray-500">Budget:</span>
              <div className="flex items-center space-x-1.5">
                <span className="text-gray-950 font-semibold">{formatBudget(details["Budget (Cr)"])}</span>
                <span>{matchDetails.budget ? '✅' : '❌'}</span>
              </div>
            </div>

            {/* Location */}
            <div className="flex items-center justify-between">
              <span className="font-medium text-gray-500">Location:</span>
              <div className="flex items-center space-x-1.5">
                <span className="text-gray-950 font-semibold">{details["Location"] || 'N/A'}</span>
                <span>{matchDetails.location ? '✅' : '❌'}</span>
              </div>
            </div>

            {/* Status */}
            <div className="flex items-center justify-between">
              <span className="font-medium text-gray-500">Status:</span>
              <div className="flex items-center space-x-1.5">
                <span className="text-gray-950 font-semibold">{details["Status"] || 'N/A'}</span>
                <span>{matchDetails.status ? '✅' : '❌'}</span>
              </div>
            </div>
          </div>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="w-full bg-gray-50 hover:bg-gray-100 text-gray-700 font-semibold py-2.5 px-4 rounded-lg border border-gray-200 transition text-sm flex items-center justify-center space-x-1"
        >
          <span>VIEW FULL DETAILS</span>
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>

      {/* Modal Dialog */}
      {showModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full shadow-2xl overflow-hidden animate-fade-in">
            <div className="bg-gray-50 border-b border-gray-100 px-6 py-4 flex justify-between items-center">
              <h3 className="text-xl font-bold text-gray-900">
                {details["Project Name"] || "Property Detailed View"}
              </h3>
              <button
                onClick={() => setShowModal(false)}
                className="text-gray-400 hover:text-gray-600 focus:outline-none text-2xl"
              >
                &times;
              </button>
            </div>
            
            <div className="p-6 max-h-[70vh] overflow-y-auto space-y-4">
              <div className="grid grid-cols-2 gap-4">
                {Object.entries(details).map(([key, value]) => (
                  <div key={key} className="border-b border-gray-100 pb-2 col-span-2 sm:col-span-1">
                    <span className="block text-xs font-semibold text-gray-400 uppercase tracking-wider">{key}</span>
                    <span className="text-gray-900 font-medium text-sm leading-relaxed">
                      {value === null || value === undefined ? (
                        <em className="text-gray-300">N/A</em>
                      ) : (
                        String(value)
                      )}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-gray-50 px-6 py-4 border-t border-gray-100 flex justify-end">
              <button
                onClick={() => setShowModal(false)}
                className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-2 rounded-lg transition"
              >
                Close Details
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
