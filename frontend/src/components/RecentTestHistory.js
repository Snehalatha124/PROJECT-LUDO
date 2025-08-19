import React from 'react';
import { useTestContext } from '../context/TestContext';
import { History, AlertTriangle, X } from 'lucide-react';

const RecentTestHistory = () => {
  const { testHistory, removeTestFromHistory } = useTestContext();

  const handleDeleteTest = (index) => {
    if (removeTestFromHistory) {
      removeTestFromHistory(index);
    }
  };

  return (
    <div className="flex-1 min-w-0">
      <div className="card h-full">
        <div className="flex items-center space-x-3 mb-4">
          <History className="h-6 w-6 text-orange-400" />
          <h3 className="text-lg font-semibold text-white">Recent Test History</h3>
        </div>
        
        <div className="space-y-4">
                     {testHistory && testHistory.length > 0 ? (
             testHistory.map((test, index) => (
               <div key={index} className="border border-gray-700 rounded-lg p-3 relative">
                 {/* Delete Button */}
                 <button
                   onClick={() => handleDeleteTest(index)}
                   className="absolute top-2 right-2 p-1 rounded-full bg-red-500/20 hover:bg-red-500/40 transition-colors group"
                   title="Delete test"
                 >
                   <X className="h-3 w-3 text-red-400 group-hover:text-red-300" />
                 </button>
                 
                 <div className="flex items-center space-x-2 mb-2">
                   <AlertTriangle className="h-4 w-4 text-yellow-400" />
                   <span className="font-semibold text-white">{test.type} - {test.users} Users</span>
                 </div>
                 <p className="text-gray-300 text-sm mb-2">
                   Good performance with minor issues with {test.success_rate}% success rate
                 </p>
                 <div className="text-gray-400 text-sm">
                   Avg Response: {test.avg_response_time}ms | Transaction Per Second: {test.peak_rps}
                 </div>
                 <div className="text-gray-500 text-xs mt-1">
                   {test.timestamp}
                 </div>
               </div>
             ))
          ) : (
            <div className="text-center py-8">
              <History className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-400">No test history available</p>
              <p className="text-sm text-gray-500">Run tests to see history</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RecentTestHistory; 