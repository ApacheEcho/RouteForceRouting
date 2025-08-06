import React, { useState, useCallback, useEffect } from 'react';
import { Notebook, Clock, Tag, Trash2, Download, Upload } from 'lucide-react';
import VoiceRecorder from './VoiceRecorder';

interface VoiceNote {
  id: string;
  transcript: string;
  audioBlob?: Blob;
  timestamp: Date;
  tags: string[];
  category: 'idea' | 'code' | 'todo' | 'reminder' | 'other';
}

export interface VoiceNotesProps {
  onNoteSaved?: (note: VoiceNote) => void;
  className?: string;
}

export const VoiceNotes: React.FC<VoiceNotesProps> = ({
  onNoteSaved,
  className = ''
}) => {
  const [notes, setNotes] = useState<VoiceNote[]>([]);
  const [currentTranscript, setCurrentTranscript] = useState('');
  const [currentAudio, setCurrentAudio] = useState<Blob | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<VoiceNote['category']>('idea');
  const [filterCategory, setFilterCategory] = useState<VoiceNote['category'] | 'all'>('all');
  const [searchTerm, setSearchTerm] = useState('');

  // Load notes from localStorage on component mount
  useEffect(() => {
    const storedNotes = localStorage.getItem('voiceNotes');
    if (storedNotes) {
      try {
        const parsedNotes = JSON.parse(storedNotes).map((note: any) => ({
          ...note,
          timestamp: new Date(note.timestamp)
        }));
        setNotes(parsedNotes);
      } catch (error) {
        console.error('Error loading voice notes:', error);
      }
    }
  }, []);

  // Save notes to localStorage whenever notes change
  useEffect(() => {
    localStorage.setItem('voiceNotes', JSON.stringify(notes));
  }, [notes]);

  const handleTranscript = useCallback((transcript: string) => {
    setCurrentTranscript(transcript);
  }, []);

  const handleAudioComplete = useCallback((audioBlob: Blob) => {
    setCurrentAudio(audioBlob);
  }, []);

  const saveNote = useCallback(() => {
    if (!currentTranscript.trim()) return;

    const newNote: VoiceNote = {
      id: crypto.randomUUID(),
      transcript: currentTranscript.trim(),
      audioBlob: currentAudio || undefined,
      timestamp: new Date(),
      tags: extractTags(currentTranscript),
      category: selectedCategory
    };

    setNotes(prev => [newNote, ...prev]);
    setCurrentTranscript('');
    setCurrentAudio(null);
    
    if (onNoteSaved) {
      onNoteSaved(newNote);
    }
  }, [currentTranscript, currentAudio, selectedCategory, onNoteSaved]);

  const extractTags = (text: string): string[] => {
    // Extract hashtags and common keywords
    const hashtags = text.match(/#\w+/g) || [];
    const keywords = [];
    
    // Add automatic tags based on content
    if (text.toLowerCase().includes('bug') || text.toLowerCase().includes('fix')) {
      keywords.push('#bug');
    }
    if (text.toLowerCase().includes('feature') || text.toLowerCase().includes('add')) {
      keywords.push('#feature');
    }
    if (text.toLowerCase().includes('urgent') || text.toLowerCase().includes('asap')) {
      keywords.push('#urgent');
    }
    if (text.toLowerCase().includes('api')) {
      keywords.push('#api');
    }
    if (text.toLowerCase().includes('ui') || text.toLowerCase().includes('interface')) {
      keywords.push('#ui');
    }

    return [...new Set([...hashtags, ...keywords])];
  };

  const deleteNote = useCallback((noteId: string) => {
    setNotes(prev => prev.filter(note => note.id !== noteId));
  }, []);

  const exportNotes = useCallback(() => {
    const exportData = {
      notes: notes,
      exportDate: new Date().toISOString(),
      version: '1.0'
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { 
      type: 'application/json' 
    });
    
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `voice-notes-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [notes]);

  const importNotes = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const content = e.target?.result as string;
        const importData = JSON.parse(content);
        
        if (importData.notes && Array.isArray(importData.notes)) {
          const importedNotes = importData.notes.map((note: any) => ({
            ...note,
            id: crypto.randomUUID(), // Generate new IDs to avoid conflicts
            timestamp: new Date(note.timestamp)
          }));
          
          setNotes(prev => [...importedNotes, ...prev]);
        }
      } catch (error) {
        console.error('Error importing notes:', error);
        alert('Error importing notes. Please check the file format.');
      }
    };
    reader.readAsText(file);
  }, []);

  const filteredNotes = notes.filter(note => {
    const matchesCategory = filterCategory === 'all' || note.category === filterCategory;
    const matchesSearch = searchTerm === '' || 
      note.transcript.toLowerCase().includes(searchTerm.toLowerCase()) ||
      note.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    
    return matchesCategory && matchesSearch;
  });

  return (
    <div className={`bg-white border border-gray-200 rounded-lg p-6 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Notebook className="w-5 h-5 text-indigo-600" />
          <h3 className="text-lg font-semibold text-gray-900">Voice Notes</h3>
          <span className="bg-indigo-100 text-indigo-800 text-xs px-2 py-1 rounded-full">
            {notes.length} notes
          </span>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={exportNotes}
            className="flex items-center space-x-1 px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            <Download className="w-3 h-3" />
            <span>Export</span>
          </button>
          <label className="flex items-center space-x-1 px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors cursor-pointer">
            <Upload className="w-3 h-3" />
            <span>Import</span>
            <input
              type="file"
              accept=".json"
              onChange={importNotes}
              className="hidden"
            />
          </label>
        </div>
      </div>

      <div className="space-y-6">
        {/* Voice Recorder for New Notes */}
        <div className="space-y-4">
          <VoiceRecorder
            onTranscript={handleTranscript}
            onRecordingComplete={handleAudioComplete}
            placeholder="Record a voice note, idea, or reminder..."
          />

          {/* Current Note Preview */}
          {currentTranscript && (
            <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-3">
              <p className="text-sm text-indigo-800 mb-2">{currentTranscript}</p>
              <div className="flex items-center justify-between">
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value as VoiceNote['category'])}
                  className="text-sm border border-indigo-300 rounded px-2 py-1 bg-white"
                >
                  <option value="idea">💡 Idea</option>
                  <option value="code">💻 Code</option>
                  <option value="todo">✅ Todo</option>
                  <option value="reminder">⏰ Reminder</option>
                  <option value="other">📝 Other</option>
                </select>
                <button
                  onClick={saveNote}
                  className="px-4 py-1 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  Save Note
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Filters */}
        <div className="flex items-center space-x-4">
          <div className="flex-1">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search notes..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
          <select
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value as VoiceNote['category'] | 'all')}
            className="border border-gray-300 rounded-lg px-3 py-2"
          >
            <option value="all">All Categories</option>
            <option value="idea">💡 Ideas</option>
            <option value="code">💻 Code</option>
            <option value="todo">✅ Todos</option>
            <option value="reminder">⏰ Reminders</option>
            <option value="other">📝 Other</option>
          </select>
        </div>

        {/* Notes List */}
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {filteredNotes.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Notebook className="w-12 h-12 mx-auto mb-2 text-gray-300" />
              <p>No voice notes yet. Start recording to capture your ideas!</p>
            </div>
          ) : (
            filteredNotes.map((note) => (
              <div key={note.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="text-lg">
                      {note.category === 'idea' && '💡'}
                      {note.category === 'code' && '💻'}
                      {note.category === 'todo' && '✅'}
                      {note.category === 'reminder' && '⏰'}
                      {note.category === 'other' && '📝'}
                    </span>
                    <div className="flex items-center space-x-1 text-xs text-gray-500">
                      <Clock className="w-3 h-3" />
                      <span>{note.timestamp.toLocaleDateString()} {note.timestamp.toLocaleTimeString()}</span>
                    </div>
                  </div>
                  <button
                    onClick={() => deleteNote(note.id)}
                    className="text-red-500 hover:text-red-700 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
                
                <p className="text-gray-800 mb-2 whitespace-pre-wrap">{note.transcript}</p>
                
                {note.tags.length > 0 && (
                  <div className="flex items-center space-x-1 flex-wrap">
                    <Tag className="w-3 h-3 text-gray-400" />
                    {note.tags.map((tag, index) => (
                      <span key={index} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))
          )}
        </div>

        {/* Offline Tips */}
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h4 className="text-sm font-semibold text-green-900 mb-2">Offline Voice Notes:</h4>
          <ul className="text-sm text-green-800 space-y-1">
            <li>• Notes are saved locally and sync when online</li>
            <li>• Use voice notes for quick idea capture during commutes</li>
            <li>• Export notes to share with your development team</li>
            <li>• Tag notes with #urgent, #feature, #bug for organization</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default VoiceNotes;