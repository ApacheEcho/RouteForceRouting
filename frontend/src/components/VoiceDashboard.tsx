import React, { useState, useCallback } from 'react';
import { Mic, GitCommit, Code, Notebook, Settings, Smartphone, Headphones } from 'lucide-react';
import { VoiceRecorder, VoiceCommit, VoiceCoding, VoiceNotes } from './VoiceInput';

interface VoiceDashboardProps {
  className?: string;
}

export const VoiceDashboard: React.FC<VoiceDashboardProps> = ({
  className = ''
}) => {
  const [activeTab, setActiveTab] = useState<'commit' | 'coding' | 'notes' | 'mobile'>('commit');
  const [isVoiceEnabled, setIsVoiceEnabled] = useState(true);
  const [voiceSettings, setVoiceSettings] = useState({
    autoSave: true,
    pushToTalk: false,
    noiseReduction: true,
    language: 'en-US'
  });

  const handleCommit = useCallback(async (message: string, files?: string[]) => {
    try {
      // In a real implementation, this would integrate with Git API
      console.log('Committing with message:', message, 'Files:', files);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Show success message
      alert(`Commit successful: "${message}"`);
    } catch (error) {
      console.error('Commit failed:', error);
      alert('Commit failed. Please try again.');
    }
  }, []);

  const handleCodeGenerated = useCallback((code: string, language: string, filename?: string) => {
    console.log('Code generated:', { code, language, filename });
    
    // In a real implementation, this would save to file system or send to editor
    if (filename) {
      // Create a downloadable file
      const blob = new Blob([code], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } else {
      // Copy to clipboard
      navigator.clipboard.writeText(code).then(() => {
        alert('Code copied to clipboard!');
      });
    }
  }, []);

  const tabs = [
    { id: 'commit', label: 'Voice Commits', icon: GitCommit, color: 'green' },
    { id: 'coding', label: 'Voice Coding', icon: Code, color: 'purple' },
    { id: 'notes', label: 'Voice Notes', icon: Notebook, color: 'indigo' },
    { id: 'mobile', label: 'Mobile Setup', icon: Smartphone, color: 'blue' }
  ];

  return (
    <div className={`bg-gray-50 min-h-screen ${className}`}>
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg">
              <Mic className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Voice-to-Code Dashboard</h1>
              <p className="text-gray-600 text-sm">Maximize productivity with voice coding tools</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <span className={`w-2 h-2 rounded-full ${isVoiceEnabled ? 'bg-green-500' : 'bg-red-500'}`} />
              <span className="text-sm text-gray-600">
                {isVoiceEnabled ? 'Voice Active' : 'Voice Disabled'}
              </span>
            </div>
            <button
              onClick={() => setIsVoiceEnabled(!isVoiceEnabled)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                isVoiceEnabled 
                  ? 'bg-red-100 text-red-700 hover:bg-red-200' 
                  : 'bg-green-100 text-green-700 hover:bg-green-200'
              }`}
            >
              {isVoiceEnabled ? 'Disable Voice' : 'Enable Voice'}
            </button>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="px-6">
          <nav className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                    isActive
                      ? `border-${tab.color}-500 text-${tab.color}-600`
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className="p-6">
        {!isVoiceEnabled && (
          <div className="mb-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-center space-x-2">
              <Settings className="w-5 h-5 text-yellow-600" />
              <p className="text-yellow-800">
                Voice features are disabled. Enable voice to use all voice-to-code functionality.
              </p>
            </div>
          </div>
        )}

        {/* Tab Content */}
        <div className="max-w-4xl">
          {activeTab === 'commit' && (
            <VoiceCommit
              onCommit={handleCommit}
              className="opacity-100"
            />
          )}

          {activeTab === 'coding' && (
            <VoiceCoding
              onCodeGenerated={handleCodeGenerated}
              className="opacity-100"
            />
          )}

          {activeTab === 'notes' && (
            <VoiceNotes className="opacity-100" />
          )}

          {activeTab === 'mobile' && (
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <div className="flex items-center space-x-2 mb-4">
                <Smartphone className="w-5 h-5 text-blue-600" />
                <h3 className="text-lg font-semibold text-gray-900">Mobile Voice Coding Setup</h3>
              </div>

              <div className="space-y-6">
                {/* PWA Instructions */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-semibold text-blue-900 mb-2">📱 Progressive Web App (PWA)</h4>
                  <ul className="text-sm text-blue-800 space-y-1">
                    <li>• Install this app on your mobile device for offline voice notes</li>
                    <li>• Voice notes sync automatically when you're back online</li>
                    <li>• Perfect for capturing ideas during commutes or meetings</li>
                  </ul>
                </div>

                {/* Wearable Integration */}
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <h4 className="font-semibold text-green-900 mb-2">⌚ Wearable Integration</h4>
                  <ul className="text-sm text-green-800 space-y-1">
                    <li>• Use smartwatch voice commands to trigger quick notes</li>
                    <li>• Set up voice shortcuts for common coding patterns</li>
                    <li>• Hands-free coding during exercise or walking meetings</li>
                  </ul>
                </div>

                {/* GitHub Copilot Voice */}
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <h4 className="font-semibold text-purple-900 mb-2">🤖 GitHub Copilot Voice Integration</h4>
                  <div className="space-y-3">
                    <p className="text-sm text-purple-800">
                      Configure GitHub Copilot Voice in VS Code for ultimate voice coding experience:
                    </p>
                    <div className="bg-purple-100 rounded p-3">
                      <code className="text-xs text-purple-900 font-mono">
                        1. Install "GitHub Copilot Voice" extension in VS Code<br/>
                        2. Enable voice commands: Ctrl+Shift+P → "Copilot: Enable Voice"<br/>
                        3. Use voice commands: "Hey GitHub, create a function that..."<br/>
                        4. Voice commit: "Hey GitHub, commit this with message..."
                      </code>
                    </div>
                  </div>
                </div>

                {/* Voice Commands Reference */}
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-3">🎤 Voice Commands Reference</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h5 className="font-medium text-gray-800 mb-2">Coding Commands:</h5>
                      <ul className="text-sm text-gray-600 space-y-1">
                        <li>• "Create function [name]"</li>
                        <li>• "Make React component [name]"</li>
                        <li>• "Add API endpoint for [purpose]"</li>
                        <li>• "Write test for [functionality]"</li>
                      </ul>
                    </div>
                    <div>
                      <h5 className="font-medium text-gray-800 mb-2">Git Commands:</h5>
                      <ul className="text-sm text-gray-600 space-y-1">
                        <li>• "Commit with message [message]"</li>
                        <li>• "Add all files and commit"</li>
                        <li>• "Create branch [name]"</li>
                        <li>• "Push to remote"</li>
                      </ul>
                    </div>
                  </div>
                </div>

                {/* Productivity Tips */}
                <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
                  <div className="flex items-center space-x-2 mb-3">
                    <Headphones className="w-5 h-5 text-indigo-600" />
                    <h4 className="font-semibold text-indigo-900">🚀 Productivity Maximization Tips</h4>
                  </div>
                  <ul className="text-sm text-indigo-800 space-y-2">
                    <li>• <strong>Commute Coding:</strong> Use voice notes to capture architecture ideas while traveling</li>
                    <li>• <strong>Meeting Notes:</strong> Record technical discussions and convert to action items</li>
                    <li>• <strong>Code Reviews:</strong> Dictate review comments while reviewing code</li>
                    <li>• <strong>Documentation:</strong> Create API docs and README files through voice dictation</li>
                    <li>• <strong>Debugging:</strong> Voice-log debugging steps and solutions for future reference</li>
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VoiceDashboard;