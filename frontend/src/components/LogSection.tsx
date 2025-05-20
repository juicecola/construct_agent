import React from 'react';
import { HazardLogEntry, AttendanceLogEntry, DeliveryLogEntry } from '../types/logTypes';
import LogCard from './LogCard'; // Import the new card component

interface LogSectionProps {
  title: string;
  logs: Array<HazardLogEntry | AttendanceLogEntry | DeliveryLogEntry>;
  type: 'hazard' | 'attendance' | 'delivery';
}

const LogSection: React.FC<LogSectionProps> = ({ title, logs = [], type }) => {
  return (
    // Removed fixed height and overflow, let content determine height, or set min-height
    <div className="bg-gray-100 p-4 rounded-lg shadow-inner border border-gray-200 min-h-[200px]">
      <h2 className="text-xl font-semibold mb-3 border-b border-gray-300 pb-2 text-gray-700 flex justify-between items-center">
        <span>{title}</span>
        {/* Display count */}
        <span className="text-sm font-medium bg-gray-200 text-gray-600 rounded-full px-2 py-0.5">
          {logs.length}
        </span>
      </h2>
      {logs.length === 0 ? (
        <p className="text-gray-500 italic text-sm text-center pt-4">No {type} logs yet.</p>
      ) : (
        // Use space-y for vertical spacing between cards
        <div className="space-y-3 max-h-96 overflow-y-auto pr-2"> {/* Add max-height and scroll if needed */}
          {logs.map((log, index) => (
            <LogCard
              key={`${type}-${log.timestamp}-${index}`} // Consider a more stable key if possible
              log={log}
              type={type}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default LogSection;