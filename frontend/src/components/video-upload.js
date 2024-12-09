import React, { useState } from 'react';
import { ChevronDownIcon, FileIcon } from 'lucide-react';
import { VIDEO_TITLES } from '../config/videoConfig';

export default function VideoUpload() {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  // Fixed lectures list
  const lectures = [
    { id: 'L1', title: VIDEO_TITLES['L1'] },
    { id: 'L2', title: VIDEO_TITLES['L2'] },
    { id: 'L3', title: VIDEO_TITLES['L3'] },
    { id: 'L4', title: VIDEO_TITLES['L4'] }
  ];

  return (
    <div className="absolute top-4 right-4 flex items-center gap-2 z-10">
      {/* Lectures Dropdown */}
      <div className="relative">
        <button
          onClick={() => setIsDropdownOpen(!isDropdownOpen)}
          className="flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
        >
          Available Lectures
          <ChevronDownIcon className="w-4 h-4 ml-2" />
        </button>

        {isDropdownOpen && (
          <div className="absolute right-0 mt-2 w-96 bg-white rounded-md shadow-lg z-50">
            <div className="py-1">
              {lectures.map((lecture) => (
                <div key={lecture.id} className="flex items-center px-4 py-2 hover:bg-gray-50">
                  <div className="flex-1">
                    <div className="flex items-center">
                      <FileIcon className="h-5 w-5 text-gray-500 mr-2" />
                      <span className="text-sm text-gray-700">{lecture.title}</span>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      Lecture {lecture.id}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 