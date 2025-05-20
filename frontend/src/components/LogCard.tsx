import React from 'react';
import { HazardLogEntry, AttendanceLogEntry, DeliveryLogEntry } from '../types/logTypes';
// Import icons (choose icons you like)
import { GoAlert } from "react-icons/go"; // Hazard (Github Octicons)
import { FiUserCheck, FiUserMinus, FiPackage } from "react-icons/fi"; // Attendance, Delivery (Feather Icons)
import { MdErrorOutline } from "react-icons/md"; // Fallback/Error Icon

type LogCardProps = {
  log: HazardLogEntry | AttendanceLogEntry | DeliveryLogEntry;
  type: 'hazard' | 'attendance' | 'delivery';
};

const LogCard: React.FC<LogCardProps> = ({ log, type }) => {
  // Determine icon and color based on type and content
  let IconComponent: React.ElementType = MdErrorOutline; // Default icon
  let iconColor = 'text-gray-500';
  let borderColor = 'border-gray-300';
  let title = 'Log Entry';

  if (type === 'hazard') {
    IconComponent = GoAlert;
    iconColor = 'text-red-600';
    borderColor = 'border-red-500';
    title = 'Hazard Report';
  } else if (type === 'attendance') {
    const attendanceLog = log as AttendanceLogEntry;
    if (attendanceLog.action === 'Check-In') {
      IconComponent = FiUserCheck;
      iconColor = 'text-green-600';
      borderColor = 'border-green-500';
      title = 'Worker Check-In';
    } else {
      IconComponent = FiUserMinus;
      iconColor = 'text-yellow-600';
      borderColor = 'border-yellow-500';
      title = 'Worker Check-Out';
    }
  } else if (type === 'delivery') {
    IconComponent = FiPackage;
    iconColor = 'text-purple-600';
    borderColor = 'border-purple-500';
    title = 'Delivery Confirmation';
  }

  // Format details based on type
  const renderDetails = () => {
    const timestamp = log.timestamp || 'Timestamp missing'; // Basic fallback


    switch (type) {
      case 'hazard': {
        const hazardLog = log as HazardLogEntry;
        return (
          <>
            <p className="font-semibold text-gray-700">{hazardLog.description ?? 'No description'}</p>
            <p className="text-sm text-gray-600">Location: {hazardLog.location ?? 'N/A'}</p>
            <p className="text-xs text-gray-500 mt-1">Reported by: {hazardLog.reporter ?? 'N/A'} - {timestamp}</p>
          </>
        );
      }
      case 'attendance': {
        const attendanceLog = log as AttendanceLogEntry;
        return (
          <>
            <p className="font-semibold text-gray-700">Worker: {attendanceLog.worker_id ?? 'N/A'}</p>
            <p className="text-sm text-gray-600">Phone: {attendanceLog.phone ?? 'N/A'}</p>
            <p className="text-xs text-gray-500 mt-1">Action: {attendanceLog.action ?? 'N/A'} - {timestamp}</p>
          </>
        );
      }
      case 'delivery': {
        const deliveryLog = log as DeliveryLogEntry;
        return (
          <>
            <p className="font-semibold text-gray-700">Order/Material: {deliveryLog.order_id ?? 'N/A'}</p>
            <p className="text-sm text-gray-600">Location: {deliveryLog.location ?? 'N/A'}</p>
            <p className="text-sm text-gray-600">Details: {deliveryLog.details ?? 'N/A'}</p>
            <p className="text-xs text-gray-500 mt-1">{timestamp}</p>
          </>
        );
      }
      default:
        return <p className="text-gray-500">Invalid log data</p>;
    }
  };

  return (
    <div className={`bg-white rounded-lg shadow hover:shadow-md transition-shadow duration-200 border-l-4 ${borderColor} p-4 flex space-x-4 items-start`}>
      <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${iconColor} bg-opacity-10 ${borderColor.replace('border-', 'bg-').replace('-500', '-100')}`}>
         {/* Icon size and color */}
        <IconComponent size={24} className={iconColor} />
      </div>
      <div className="flex-grow">
        <h4 className="font-bold text-sm text-gray-800 mb-1">{title}</h4>
        <div className="text-sm">
          {renderDetails()}
        </div>
      </div>
    </div>
  );
};

export default LogCard;