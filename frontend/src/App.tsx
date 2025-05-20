import React, { useState, useEffect } from 'react';
import axios, { AxiosError } from 'axios';
import LogSection from './components/LogSection'; // Ensure this path is correct
import { HazardLogEntry, AttendanceLogEntry, DeliveryLogEntry } from './types/logTypes';
import { FaSpinner } from 'react-icons/fa'; // Loading spinner icon

// --- IMPORTANT: Replace with your ngrok URL ---
const API_BASE_URL: string = 'https://b750-41-139-168-163.ngrok-free.app';

function App(): JSX.Element {
  const [hazards, setHazards] = useState<HazardLogEntry[]>([]);
  const [attendance, setAttendance] = useState<AttendanceLogEntry[]>([]);
  const [deliveries, setDeliveries] = useState<DeliveryLogEntry[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async (): Promise<void> => {
    // Don't reset loading to true on subsequent polls if you want a smoother update
    // setLoading(true);
    // setError(null); // Keep previous error state until successful fetch? Or clear always?

    try {
      const [hazardsRes, attendanceRes, deliveriesRes] = await Promise.all([
        axios.get<HazardLogEntry[]>(`${API_BASE_URL}/api/hazards`),
        axios.get<AttendanceLogEntry[]>(`${API_BASE_URL}/api/attendance`),
        axios.get<DeliveryLogEntry[]>(`${API_BASE_URL}/api/deliveries`)
      ]);

      setHazards(hazardsRes.data.reverse());
      setAttendance(attendanceRes.data.reverse());
      setDeliveries(deliveriesRes.data.reverse());
      setError(null); // Clear error only on success

    } catch (err) {
      console.error("Error fetching data:", err);
      let errorMessage = "Failed to fetch data. Check backend logs and ngrok status.";
      // ... (keep existing error handling logic) ...
       if (axios.isAxiosError(err)) {
            const axiosError = err as AxiosError;
            if (axiosError.response) {
              errorMessage = `Backend error: ${axiosError.response.status} ${axiosError.response.statusText}`;
            } else if (axiosError.request) {
              errorMessage = `Network Error: Could not connect to the backend at ${API_BASE_URL}. Is it running? Check CORS settings.`;
            }
          } else if (err instanceof Error) {
             errorMessage = err.message;
          }
      setError(errorMessage);
    } finally {
      // Set loading to false only after the *initial* fetch
      if (loading) setLoading(false);
    }
  };

  useEffect(() => {
    fetchData(); // Initial fetch
    const intervalId = setInterval(fetchData, 15000); // Poll every 15 seconds
    return () => clearInterval(intervalId);
  }, []); // Rerun effect logic only if the base URL were to change (it won't here)

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-100 to-blue-50"> {/* Added gradient bg */}
      <div className="container mx-auto p-4 md:p-6 lg:p-8 max-w-7xl"> {/* Increased max-width */}
        <header className="mb-8 text-center">
           {/* You could add a logo here */}
          <h1 className="text-3xl md:text-4xl font-bold text-gray-800">
            ConstructAgent Dashboard
          </h1>
          <p className="text-gray-600 mt-1">Real-time Site Monitoring</p>
        </header>


        {/* Loading State */}
        {loading && (
          <div className="flex justify-center items-center py-10">
            <FaSpinner className="animate-spin text-4xl text-blue-500 mr-3" />
            <span className="text-xl text-gray-600">Loading initial data...</span>
          </div>
        )}

        {/* Error State */}
        {error && !loading && ( // Show error only if not loading initially
          <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded-md shadow my-6" role="alert">
            <p className="font-bold">Error</p>
            <p>{error}</p>
          </div>
        )}

        {/* Content Area */}
        {!loading && !error && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <LogSection title="Hazard Reports" logs={hazards} type="hazard" />
            <LogSection title="Attendance Log" logs={attendance} type="attendance" />
            <LogSection title="Delivery Confirmations" logs={deliveries} type="delivery" />
          </div>
        )}

        <footer className="text-center mt-12 text-gray-500 text-sm">
          Powered by Africa's Talking & Google Cloud
        </footer>
      </div>
    </div>
  );
}

export default App;