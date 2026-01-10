// File: frontend/src/components/RatingWidget.jsx

import { useState } from 'react';
import { Star } from 'lucide-react';

export default function RatingWidget({ referenceId, onRate }) {
  const [rating, setRating] = useState(0);
  const [hover, setHover] = useState(0);
  const [comment, setComment] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (rating === 0) return;

    await onRate(referenceId, rating, comment);
    setSubmitted(true);
  };

  if (submitted) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <p className="text-green-700 font-medium">Thank you for your rating!</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-bold text-gray-900 mb-4">Rate This Source</h3>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Star rating */}
        <div className="flex items-center space-x-1">
          {[1, 2, 3, 4, 5].map((star) => (
            <button
              key={star}
              type="button"
              onClick={() => setRating(star)}
              onMouseEnter={() => setHover(star)}
              onMouseLeave={() => setHover(0)}
              className="focus:outline-none"
            >
              <Star
                className={`h-8 w-8 ${
                  star <= (hover || rating)
                    ? 'text-yellow-400 fill-yellow-400'
                    : 'text-gray-300'
                }`}
              />
            </button>
          ))}
        </div>

        {/* Comment */}
        <textarea
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="Add a comment (optional)"
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
        />

        {/* Submit */}
        <button
          type="submit"
          disabled={rating === 0}
          className="w-full bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Submit Rating
        </button>
      </form>
    </div>
  );
}