import React, { useState, useCallback } from 'react';
import { Code, FileText, Lightbulb, Save } from 'lucide-react';
import VoiceRecorder from './VoiceRecorder';

interface VoiceCodingProps {
  onCodeGenerated: (code: string, language: string, filename?: string) => void;
  className?: string;
}

export const VoiceCoding: React.FC<VoiceCodingProps> = ({
  onCodeGenerated,
  className = ''
}) => {
  const [voiceInput, setVoiceInput] = useState('');
  const [generatedCode, setGeneratedCode] = useState('');
  const [language, setLanguage] = useState('javascript');
  const [filename, setFilename] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  const processVoiceToCode = useCallback((transcript: string) => {
    setIsProcessing(true);
    
    // Process voice commands for code generation
    let processedInput = transcript
      .replace(/\bnew line\b/gi, '\n')
      .replace(/\btab\b/gi, '    ')
      .replace(/\bopen brace\b/gi, '{')
      .replace(/\bclose brace\b/gi, '}')
      .replace(/\bopen bracket\b/gi, '[')
      .replace(/\bclose bracket\b/gi, ']')
      .replace(/\bopen paren\b/gi, '(')
      .replace(/\bclose paren\b/gi, ')')
      .replace(/\bsemicolon\b/gi, ';')
      .replace(/\bcomma\b/gi, ',')
      .replace(/\bperiod\b/gi, '.')
      .replace(/\bequals\b/gi, '=')
      .replace(/\bplus\b/gi, '+')
      .replace(/\bminus\b/gi, '-')
      .replace(/\basterisk\b/gi, '*')
      .replace(/\bslash\b/gi, '/')
      .replace(/\bquote\b/gi, '"')
      .replace(/\bsingle quote\b/gi, "'");

    // Auto-detect language from voice commands
    if (transcript.toLowerCase().includes('react') || transcript.toLowerCase().includes('jsx')) {
      setLanguage('jsx');
    } else if (transcript.toLowerCase().includes('python') || transcript.toLowerCase().includes('def ')) {
      setLanguage('python');
    } else if (transcript.toLowerCase().includes('typescript') || transcript.toLowerCase().includes('interface')) {
      setLanguage('typescript');
    } else if (transcript.toLowerCase().includes('css') || transcript.toLowerCase().includes('style')) {
      setLanguage('css');
    }

    // Generate code based on common patterns
    let code = '';
    
    if (transcript.toLowerCase().includes('function') || transcript.toLowerCase().includes('create function')) {
      code = generateFunction(processedInput, language);
    } else if (transcript.toLowerCase().includes('component') && language.includes('jsx')) {
      code = generateReactComponent(processedInput);
    } else if (transcript.toLowerCase().includes('api') || transcript.toLowerCase().includes('endpoint')) {
      code = generateApiEndpoint(processedInput, language);
    } else if (transcript.toLowerCase().includes('class')) {
      code = generateClass(processedInput, language);
    } else {
      code = processedInput; // Fallback to processed voice input
    }

    setGeneratedCode(code);
    setVoiceInput(processedInput);
    setIsProcessing(false);
  }, [language]);

  const generateFunction = (input: string, lang: string): string => {
    const functionName = extractFunctionName(input);
    
    switch (lang) {
      case 'javascript':
      case 'jsx':
        return `function ${functionName}() {\n    // ${input}\n    \n}`;
      case 'typescript':
        return `function ${functionName}(): void {\n    // ${input}\n    \n}`;
      case 'python':
        return `def ${functionName}():\n    """${input}"""\n    pass`;
      default:
        return `// ${input}\nfunction ${functionName}() {\n    \n}`;
    }
  };

  const generateReactComponent = (input: string): string => {
    const componentName = extractComponentName(input);
    return `import React from 'react';

interface ${componentName}Props {
  // Define props here
}

export const ${componentName}: React.FC<${componentName}Props> = () => {
  // ${input}
  
  return (
    <div>
      <h1>${componentName}</h1>
    </div>
  );
};

export default ${componentName};`;
  };

  const generateApiEndpoint = (input: string, lang: string): string => {
    if (lang === 'python') {
      return `from flask import Blueprint, request, jsonify

api_bp = Blueprint('api', __name__)

@api_bp.route('/endpoint', methods=['GET', 'POST'])
def handle_request():
    """${input}"""
    try:
        # Implementation here
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500`;
    } else {
      return `// ${input}
export const apiEndpoint = async (req, res) => {
  try {
    // Implementation here
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};`;
    }
  };

  const generateClass = (input: string, lang: string): string => {
    const className = extractClassName(input);
    
    if (lang === 'python') {
      return `class ${className}:
    """${input}"""
    
    def __init__(self):
        pass`;
    } else {
      return `class ${className} {
    // ${input}
    
    constructor() {
        
    }
}`;
    }
  };

  const extractFunctionName = (input: string): string => {
    const match = input.match(/(\w+)\s*function|function\s*(\w+)/i);
    return match ? (match[1] || match[2]) : 'newFunction';
  };

  const extractComponentName = (input: string): string => {
    const match = input.match(/(\w+)\s*component|component\s*(\w+)/i);
    return match ? (match[1] || match[2]) : 'NewComponent';
  };

  const extractClassName = (input: string): string => {
    const match = input.match(/(\w+)\s*class|class\s*(\w+)/i);
    return match ? (match[1] || match[2]) : 'NewClass';
  };

  const handleSaveCode = useCallback(() => {
    if (generatedCode) {
      onCodeGenerated(generatedCode, language, filename);
    }
  }, [generatedCode, language, filename, onCodeGenerated]);

  return (
    <div className={`bg-white border border-gray-200 rounded-lg p-6 ${className}`}>
      <div className="flex items-center space-x-2 mb-4">
        <Code className="w-5 h-5 text-purple-600" />
        <h3 className="text-lg font-semibold text-gray-900">Voice Coding</h3>
      </div>

      <div className="space-y-4">
        {/* Voice Recorder */}
        <VoiceRecorder
          onTranscript={processVoiceToCode}
          onRecordingComplete={() => {}}
          placeholder="Describe the code you want to create..."
        />

        {/* Language Selection */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Language:
            </label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="javascript">JavaScript</option>
              <option value="typescript">TypeScript</option>
              <option value="jsx">React (JSX)</option>
              <option value="python">Python</option>
              <option value="css">CSS</option>
              <option value="html">HTML</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Filename (Optional):
            </label>
            <input
              type="text"
              value={filename}
              onChange={(e) => setFilename(e.target.value)}
              placeholder="component.tsx"
              className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Voice Input Display */}
        {voiceInput && (
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              Voice Input:
            </label>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <p className="text-sm text-blue-800">{voiceInput}</p>
            </div>
          </div>
        )}

        {/* Generated Code */}
        {generatedCode && (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="block text-sm font-medium text-gray-700">
                Generated Code:
              </label>
              <button
                onClick={handleSaveCode}
                className="flex items-center space-x-1 px-3 py-1 bg-purple-600 text-white text-sm rounded-lg hover:bg-purple-700 transition-colors"
              >
                <Save className="w-3 h-3" />
                <span>Save Code</span>
              </button>
            </div>
            <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
              <pre className="text-sm text-green-400 font-mono">
                <code>{generatedCode}</code>
              </pre>
            </div>
          </div>
        )}

        {/* Processing Indicator */}
        {isProcessing && (
          <div className="flex items-center space-x-2 text-purple-600">
            <div className="animate-spin w-4 h-4 border-2 border-purple-600 border-t-transparent rounded-full" />
            <span className="text-sm">Processing voice input...</span>
          </div>
        )}

        {/* Voice Coding Tips */}
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Lightbulb className="w-4 h-4 text-purple-600" />
            <h4 className="text-sm font-semibold text-purple-900">Voice Coding Tips:</h4>
          </div>
          <ul className="text-sm text-purple-800 space-y-1">
            <li>• Say "create function calculateTotal" for functions</li>
            <li>• Say "make React component UserProfile" for components</li>
            <li>• Say "build API endpoint for user login" for APIs</li>
            <li>• Say "create class DataProcessor" for classes</li>
            <li>• Speak punctuation: "open brace", "semicolon", "new line"</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default VoiceCoding;