import { VIDEO_MAPPINGS } from '../config/videoConfig';

const formatTimestamp = (timestamp) => {
  if (!timestamp) return 0;
  // Split timestamp into parts (HH:MM:SS.mmm)
  const [time] = timestamp.split('.');  // Remove microseconds
  const [hours, minutes, seconds] = time.split(':').map(Number);
  
  // Convert to total seconds: (hours * 3600) + (minutes * 60) + seconds
  return (hours * 3600) + (minutes * 60) + seconds;
};

const formatDisplayTimestamp = (timestamp, videoId) => {
  if (!timestamp) return 'Timestamp not available';
  
  // Split timestamp into parts (HH:MM:SS.mmm)
  const [time] = timestamp.split('.');  // Remove microseconds
  const [hours, minutes, seconds] = time.split(':').map(Number);
  
  // If hours is 0, just show minutes:seconds
  if (hours === 0) {
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  }
  // Otherwise show hours:minutes:seconds
  return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
};

const handleWatchClick = (timestamp, videoId) => {
  const videoUrl = VIDEO_MAPPINGS[videoId];
  if (videoUrl && timestamp) {
    const timeInSeconds = formatTimestamp(timestamp);
    window.open(`${videoUrl}&t=${timeInSeconds}`, '_blank');
  }
};

export { handleWatchClick, formatDisplayTimestamp }; 