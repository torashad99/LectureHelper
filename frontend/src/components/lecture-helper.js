import { SearchIcon, PlayCircleIcon, ClockIcon, ChevronUpIcon, ChevronDownIcon } from "lucide-react";
import React, { useState } from "react";
import { handleWatchClick, formatDisplayTimestamp } from '../utils/videoUtils';
import { VIDEO_TITLES } from '../config/videoConfig';
import VideoUpload from '../components/video-upload';

export default function LectureHelper() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [videos, setVideos] = useState(() => {
    return [
      { id: 'L1', title: VIDEO_TITLES[0] },
      { id: 'L2', title: VIDEO_TITLES[1] },
      { id: 'L3', title: VIDEO_TITLES[2] },
      { id: 'L4', title: VIDEO_TITLES[3] }
    ];
  });
  const [expandedResponses, setExpandedResponses] = useState({});

  const handleSearch = async (e) => {
    e.preventDefault();
    setHasSearched(true);
    
    if (!query.trim() || videos.length === 0) {
      setResults([]);
      return;
    }

    try {
      setIsLoading(true);
      const videoIdsParam = videos.map(v => `video_ids[]=${encodeURIComponent(v.id)}`).join('&');
      console.log('Searching with params:', videoIdsParam);
      
      const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&${videoIdsParam}`);
      const data = await response.json();
      console.log('Raw backend response:', data);
      
      if (response.ok && data.success && data.results) {
        const transformedResults = data.results.map(result => ({
          timestamp: result.timestamp,
          title: VIDEO_TITLES[result.lecture] || `Unknown Lecture`,
          videoId: result.lecture,
          response: result.response
        }));
        console.log('Transformed results:', transformedResults);
        setResults(transformedResults);
      } else {
        console.error('Invalid response format:', data);
        setResults([]);
      }
    } catch (error) {
      console.error('Search failed:', error);
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleResponse = (index) => {
    setExpandedResponses(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <main className="max-w-4xl mx-auto">
        <div className="mb-8 text-center">
          <div className="relative pt-16">
            <h1 className="text-3xl md:text-4xl font-bold mb-4">
              Lecture Helper
            </h1>
            <p className="text-gray-600">
              Find exactly where topics are discussed across all lectures
            </p>
            <VideoUpload 
              videos={videos}
              setVideos={setVideos}
              readOnly={true}
            />
          </div>
        </div>

        <form onSubmit={handleSearch} className="mb-8">
          <div className="relative">
            <label htmlFor="search" className="sr-only">
              Search for a topic
            </label>
            <input
              id="search"
              type="search"
              placeholder="Search any topic in the lectures..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              autoComplete="off"
              autoFocus
              className="w-full p-4 pr-24 rounded-lg border border-gray-300 shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            />
            <button
              type="submit"
              className="absolute right-2 top-1/2 transform -translate-y-1/2 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
              disabled={isLoading}
            >
              {isLoading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
              ) : (
                <SearchIcon className="w-5 h-5" />
              )}
            </button>
          </div>
        </form>

        <div className="space-y-4">
          {results
            .filter(result => result.response && result.response !== "This is not a relevant question. Please ask a different question.")
            .map((result, index) => (
              <div key={index} className="bg-white p-4 rounded-lg shadow-sm hover:shadow-md transition-shadow">
                <div className="flex justify-between items-center mb-3">
                  <div>
                    <h3 className="text-lg font-bold text-gray-900 mb-1">
                      {result.title || `Lecture ${result.videoId.substring(1)}`}
                    </h3>
                    <div className="flex items-center text-sm text-gray-500">
                      <ClockIcon className="w-4 h-4 mr-2" />
                      <span>{formatDisplayTimestamp(result.timestamp, result.videoId, query)}</span>
                    </div>
                  </div>
                  <button
                    onClick={() => handleWatchClick(result.timestamp, result.videoId, query)}
                    className="text-blue-600 hover:text-blue-700"
                  >
                    <PlayCircleIcon className="w-5 h-5" />
                  </button>
                </div>
                <div className="text-gray-700">
                  <p className={expandedResponses[index] ? '' : 'line-clamp-3'}>
                    {result.response}
                  </p>
                  {result.response && result.response.length > 200 && (
                    <button
                      onClick={() => toggleResponse(index)}
                      className="text-blue-500 hover:text-blue-600 text-sm mt-2 flex items-center"
                    >
                      {expandedResponses[index] ? (
                        <>Show less <ChevronUpIcon className="w-4 h-4 ml-1" /></>
                      ) : (
                        <>Show more <ChevronDownIcon className="w-4 h-4 ml-1" /></>
                      )}
                    </button>
                  )}
                </div>
              </div>
            ))}
          {hasSearched && query && !isLoading && results.length === 0 && (
            <p className="text-center text-gray-500">No matching content found in lectures</p>
          )}
        </div>
      </main>
    </div>
  );
}
