import { SearchIcon, PlayCircleIcon, ClockIcon } from "lucide-react";
import React from "react";

export default function LectureHelper() {
  return (
    <div className="w-full min-h-screen bg-gray-100 p-4 md:p-8">
      <main className="max-w-4xl mx-auto">
        <div className="mb-8 text-center">
          <h1 className="text-3xl md:text-4xl font-bold mb-4">
            Lecture Helper
          </h1>
          <p className="text-gray-600">
            Find exactly where topics are discussed in your lectures
          </p>
        </div>

        <div className="relative mb-8">
          <label htmlFor="search" className="sr-only">
            Search for a topic
          </label>
          <input
            id="search"
            type="text"
            placeholder="Search for a topic..."
            className="w-full p-4 pr-12 rounded-lg border border-gray-300 shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
          />
          <SearchIcon className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
        </div>

        <div className="space-y-4">
          <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">
                Introduction to Neural Networks
              </h3>
              <span className="text-sm text-gray-500">Lecture 3</span>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center text-gray-600">
                <ClockIcon className="w-4 h-4 mr-2" />
                <span>15:30</span>
              </div>
              <button
                aria-label="Watch segment starting at 15:30"
                className="flex items-center text-blue-600 hover:text-blue-700"
              >
                <PlayCircleIcon className="w-4 h-4 mr-2" />
                <span>Watch segment</span>
              </button>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">
                Backpropagation Explained
              </h3>
              <span className="text-sm text-gray-500">Lecture 4</span>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center text-gray-600">
                <ClockIcon className="w-4 h-4 mr-2" />
                <span>23:45</span>
              </div>
              <button
                aria-label="Watch segment starting at 23:45"
                className="flex items-center text-blue-600 hover:text-blue-700"
              >
                <PlayCircleIcon className="w-4 h-4 mr-2" />
                <span>Watch segment</span>
              </button>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Activation Functions</h3>
              <span className="text-sm text-gray-500">Lecture 3</span>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center text-gray-600">
                <ClockIcon className="w-4 h-4 mr-2" />
                <span>42:15</span>
              </div>
              <button
                aria-label="Watch segment starting at 42:15"
                className="flex items-center text-blue-600 hover:text-blue-700"
              >
                <PlayCircleIcon className="w-4 h-4 mr-2" />
                <span>Watch segment</span>
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
