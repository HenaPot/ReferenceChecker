// File: frontend/src/components/SimilarSources.jsx

export default function SimilarSources({ sources }) {
  if (!sources || sources.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Similar Sources</h3>
        <p className="text-gray-500">No similar sources found in our database.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-xl font-bold text-gray-900 mb-4">
        Similar Sources ({sources.length})
      </h3>
      
      <div className="space-y-3">
        {sources.map((source, index) => (
          <div key={index} className="border-l-4 border-primary-500 pl-4 py-2">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <h4 className="font-semibold text-gray-900">{source.title}</h4>
                <p className="text-sm text-gray-600">{source.domain}</p>
                <a
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-primary-600 hover:underline"
                >
                  {source.url}
                </a>
              </div>
              <div className="ml-4 text-right">
                <div className="text-sm font-medium text-gray-700">
                  Similarity: {(source.similarity * 100).toFixed(0)}%
                </div>
                <div className="text-xs text-gray-500">
                  Score: {source.credibility_score}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}