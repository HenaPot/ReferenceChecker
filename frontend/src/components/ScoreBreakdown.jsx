// File: frontend/src/components/ScoreBreakdown.jsx

export default function ScoreBreakdown({ report }) {
  const strategies = [
    {
      name: 'Domain Reputation',
      score: report.domain_score,
      max: 30,
      explanation: report.domain_explanation,
      color: 'blue'
    },
    {
      name: 'Metadata Quality',
      score: report.metadata_score,
      max: 20,
      explanation: report.metadata_explanation,
      color: 'green'
    },
    {
      name: 'Cross-References (RAG)',
      score: report.rag_score,
      max: 25,
      explanation: report.rag_explanation,
      color: 'purple'
    },
    {
      name: 'AI Content Analysis',
      score: report.ai_score,
      max: 25,
      explanation: report.ai_explanation,
      color: 'orange'
    }
  ];

  const getColorClasses = (color) => {
    const colors = {
      blue: 'bg-blue-500 text-blue-700',
      green: 'bg-green-500 text-green-700',
      purple: 'bg-purple-500 text-purple-700',
      orange: 'bg-orange-500 text-orange-700',
    };
    return colors[color] || colors.blue;
  };

  return (
    <div className="space-y-6">
      <h3 className="text-2xl font-bold text-gray-900">Score Breakdown</h3>
      
      {strategies.map((strategy, index) => (
        <div key={index} className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-start mb-2">
            <h4 className="text-lg font-semibold text-gray-900">{strategy.name}</h4>
            <span className="text-2xl font-bold text-gray-900">
              {strategy.score}/{strategy.max}
            </span>
          </div>
          
          {/* Progress bar */}
          <div className="w-full bg-gray-200 rounded-full h-3 mb-3">
            <div
              className={`h-3 rounded-full ${getColorClasses(strategy.color).split(' ')[0]}`}
              style={{ width: `${(strategy.score / strategy.max) * 100}%` }}
            ></div>
          </div>
          
          {/* Explanation */}
          <p className="text-sm text-gray-600">{strategy.explanation}</p>
        </div>
      ))}
      
      {/* Total */}
      <div className="bg-primary-50 rounded-lg shadow-lg p-6 border-2 border-primary-200">
        <div className="flex justify-between items-center">
          <h4 className="text-xl font-bold text-primary-900">Total Score</h4>
          <span className="text-3xl font-bold text-primary-900">
            {report.total_score}/100
          </span>
        </div>
      </div>
    </div>
  );
}