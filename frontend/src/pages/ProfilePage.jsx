// File: frontend/src/pages/ProfilePage.jsx

import { useAuth } from '../context/AuthContext';
import { User, Mail, Calendar } from 'lucide-react';

export default function ProfilePage() {
  const { user } = useAuth();

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Profile</h1>

      <div className="bg-white rounded-lg shadow p-8">
        <div className="flex items-center space-x-4 mb-8">
          <div className="h-20 w-20 rounded-full bg-primary-100 flex items-center justify-center">
            <User className="h-10 w-10 text-primary-600" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">{user?.email?.split('@')[0]}</h2>
            <p className="text-gray-600">Academic Researcher</p>
          </div>
        </div>

        <div className="space-y-4 border-t border-gray-200 pt-8">
          <div className="flex items-center space-x-3">
            <Mail className="h-5 w-5 text-gray-400" />
            <div>
              <p className="text-sm text-gray-500">Email</p>
              <p className="text-gray-900 font-medium">{user?.email}</p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <Calendar className="h-5 w-5 text-gray-400" />
            <div>
              <p className="text-sm text-gray-500">Member Since</p>
              <p className="text-gray-900 font-medium">
                {new Date(user?.created_at).toLocaleDateString()}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}