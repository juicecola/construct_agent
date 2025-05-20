// src/types/logTypes.ts

export interface BaseLogEntry {
    timestamp: string; // Consider using Date object if you parse it
  }
  
  export interface HazardLogEntry extends BaseLogEntry {
    location: string | null;
    description: string | null;
    reporter: string | null;
  }
  
  export interface AttendanceLogEntry extends BaseLogEntry {
    worker_id: string | number | null; // Depending on what backend sends
    action: 'Check-In' | 'Check-Out' | string | null; // Be specific or allow string
    phone: string | null;
  }
  
  export interface DeliveryLogEntry extends BaseLogEntry {
    order_id: string | null;
    location: string | null;
    details: string | null;
  }
  
  // Union type for easier handling if needed, though not strictly used in current components
  export type LogEntry = HazardLogEntry | AttendanceLogEntry | DeliveryLogEntry;