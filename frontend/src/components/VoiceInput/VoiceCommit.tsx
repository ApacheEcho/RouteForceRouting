import React, { useState, useCallback } from 'react';
import { GitCommit, Send, MessageSquare } from 'lucide-react';
import VoiceRecorder from './VoiceRecorder';

interface VoiceCommitProps {
  onCommit: (message: string, files?: string[]) => Promise<void>;
  className?: string;
}

export const VoiceCommit: React.FC<VoiceCommitProps> = ({
  onCommit,
  className = ''
}) => {
  const [commitMessage, setCommitMessage] = useState('');
  const [isCommitting, setIsCommitting] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);

  const handleTranscript = useCallback((transcript: string) => {
    // Process voice commands for commit message
    let processedMessage = transcript;

    // Convert common voice patterns to proper commit format
    processedMessage = processedMessage
      .replace(/\bnew line\b/gi, '\n')
      .replace(/\bperiod\b/gi, '.')
      .replace(/\bcomma\b/gi, ',')
      .replace(/\bcolon\b/gi, ':')
      .replace(/\bsemicolon\b/gi, ';')
      .replace(/\bquestion mark\b/gi, '?')
      .replace(/\bexclamation point\b/gi, '!')
      .replace(/\bopen paren\b/gi, '(')
      .replace(/\bclose paren\b/gi, ')')
      .replace(/\bhyphen\b/gi, '-')
      .replace(/\bunderscore\b/gi, '_');

    // Auto-format common commit patterns
    if (processedMessage.toLowerCase().includes('fix') && !processedMessage.toLowerCase().startsWith('fix')) {
      processedMessage = `fix: ${processedMessage.replace(/\bfix\b/gi, '').trim()}`;
    } else if (processedMessage.toLowerCase().includes('add') && !processedMessage.toLowerCase().startsWith('add')) {
      processedMessage = `feat: ${processedMessage.replace(/\badd\b/gi, 'add').trim()}`;
    } else if (processedMessage.toLowerCase().includes('update') && !processedMessage.toLowerCase().startsWith('update')) {
      processedMessage = `chore: ${processedMessage.replace(/\bupdate\b/gi, 'update').trim()}`;
    }

    setCommitMessage(processedMessage);
  }, []);

  const handleAudioComplete = useCallback((audioBlob: Blob) => {
    // Store audio for potential transcription backup
    console.log('Audio recording completed:', audioBlob.size, 'bytes');
  }, []);

  const handleCommit = useCallback(async () => {
    if (!commitMessage.trim()) return;

    setIsCommitting(true);
    try {
      await onCommit(commitMessage, selectedFiles);
      setCommitMessage('');
      setSelectedFiles([]);
    } catch (error) {
      console.error('Commit failed:', error);
    } finally {
      setIsCommitting(false);
    }
  }, [commitMessage, selectedFiles, onCommit]);

  return (
    <div className={`bg-white border border-gray-200 rounded-lg p-6 ${className}`}>
      <div className="flex items-center space-x-2 mb-4">
        <GitCommit className="w-5 h-5 text-blue-600" />
        <h3 className="text-lg font-semibold text-gray-900">Voice Commit</h3>
      </div>

      <div className="space-y-4">
        {/* Voice Recorder */}
        <VoiceRecorder
          onTranscript={handleTranscript}
          onRecordingComplete={handleAudioComplete}
          placeholder="Dictate your commit message..."
        />

        {/* Commit Message Preview */}
        {commitMessage && (
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              Commit Message Preview:
            </label>
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
              <pre className="text-sm text-gray-800 whitespace-pre-wrap font-mono">
                {commitMessage}
              </pre>
            </div>
          </div>
        )}

        {/* Quick Edit */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">
            Edit Message (Optional):
          </label>
          <textarea
            value={commitMessage}
            onChange={(e) => setCommitMessage(e.target.value)}
            placeholder="Type or edit your commit message..."
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={3}
          />
        </div>

        {/* File Selection */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">
            Files to Commit (Optional):
          </label>
          <input
            type="text"
            value={selectedFiles.join(', ')}
            onChange={(e) => setSelectedFiles(e.target.value.split(',').map(f => f.trim()).filter(Boolean))}
            placeholder="Leave empty to commit all changes, or specify files: file1.py, file2.js"
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Commit Button */}
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-500">
            {commitMessage.length} characters
          </div>
          <button
            onClick={handleCommit}
            disabled={!commitMessage.trim() || isCommitting}
            className="flex items-center space-x-2 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {isCommitting ? (
              <>
                <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
                <span>Committing...</span>
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                <span>Commit Changes</span>
              </>
            )}
          </button>
        </div>

        {/* Voice Command Examples */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="text-sm font-semibold text-blue-900 mb-2">Voice Command Examples:</h4>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• "Fix navigation bug in header component"</li>
            <li>• "Add voice recording functionality for commits"</li>
            <li>• "Update documentation for API endpoints"</li>
            <li>• "Refactor route optimization algorithm"</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default VoiceCommit;