// File: frontend/src/components/CredibilityGauge.jsx

export default function CredibilityGauge({ score, total = 100 }) {
  const percentage = (score / total) * 100;
  
  // Determine color based on percentage
  const getColor = () => {
    if (percentage >= 80) return { bg: 'bg-green-500', text: 'text-green-700', ring: 'ring-green-200' };
    if (percentage >= 60) return { bg: 'bg-blue-500', text: 'text-blue-700', ring: 'ring-blue-200' };
    if (percentage >= 40) return { bg: 'bg-yellow-500', text: 'text-yellow-700', ring: 'ring-yellow-200' };
    if (percentage >= 20) return { bg: 'bg-orange-500', text: 'text-orange-700', ring: 'ring-orange-200' };
    return { bg: 'bg-red-500', text: 'text-red-700', ring: 'ring-red-200' };
  };

  const getLabel = () => {
    if (percentage >= 80) return 'Highly Credible';
    if (percentage >= 60) return 'Credible';
    if (percentage >= 40) return 'Questionable';
    if (percentage >= 20) return 'Unreliable';
    return 'Highly Unreliable';
  };

  const color = getColor();

  return (
    <div className="flex flex-col items-center space-y-4">
      {/* Circular gauge */}
      <div className="relative w-48 h-48">
        <svg className="transform -rotate-90 w-48 h-48">
          {/* Background circle */}
          <circle
            cx="96"
            cy="96"
            r="88"
            stroke="currentColor"
            strokeWidth="12"
            fill="none"
            className="text-gray-200"
          />
          {/* Progress circle */}
          <circle
            cx="96"
            cy="96"
            r="88"
            stroke="currentColor"
            strokeWidth="12"
            fill="none"
            strokeDasharray={`${2 * Math.PI * 88}`}
            strokeDashoffset={`${2 * Math.PI * 88 * (1 - percentage / 100)}`}
            className={color.bg.replace('bg-', 'text-')}
            strokeLinecap="round"
          />
        </svg>
        
        {/* Score text in center */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <div className={`text-5xl font-bold ${color.text}`}>
            {score}
          </div>
          <div className="text-gray-500 text-sm">out of {total}</div>
        </div>
      </div>

      {/* Label */}
      <div className={`text-xl font-semibold ${color.text}`}>
        {getLabel()}
      </div>

      {/* Percentage badge */}
      <div className={`px-4 py-1 rounded-full ${color.bg} bg-opacity-20 ${color.text} text-sm font-medium`}>
        {percentage.toFixed(0)}% Credibility
      </div>
    </div>
  );
}