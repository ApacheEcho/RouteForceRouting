import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import { Button } from '../ui/Button';
import { 
  Plus, 
  Save, 
  Play, 
  Trash2, 
  Settings, 
  ArrowRight,
  Check,
  AlertTriangle
} from 'lucide-react';

interface PlaybookRule {
  id: string;
  type: 'constraint' | 'optimization' | 'priority';
  name: string;
  condition: string;
  action: string;
  enabled: boolean;
}

interface PlaybookChain {
  id: string;
  name: string;
  description: string;
  rules: PlaybookRule[];
  status: 'draft' | 'active' | 'paused';
  lastRun?: Date;
  successRate?: number;
}

export const PlaybookGUI: React.FC = () => {
  const [chains, setChains] = useState<PlaybookChain[]>([]);
  const [selectedChain, setSelectedChain] = useState<PlaybookChain | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [saving, setSaving] = useState(false);

  // Mock data for development
  useEffect(() => {
    const mockChains: PlaybookChain[] = [
      {
        id: '1',
        name: 'Urban Delivery Optimization',
        description: 'Optimizes routes for dense urban areas with traffic constraints',
        status: 'active',
        lastRun: new Date(),
        successRate: 94.2,
        rules: [
          {
            id: 'r1',
            type: 'constraint',
            name: 'Avoid Highway Rush Hours',
            condition: 'time >= 07:00 AND time <= 09:00',
            action: 'avoid_highways = true',
            enabled: true
          },
          {
            id: 'r2',
            type: 'optimization',
            name: 'Minimize Fuel Consumption',
            condition: 'distance > 50km',
            action: 'optimize_for = fuel_efficiency',
            enabled: true
          }
        ]
      },
      {
        id: '2',
        name: 'Suburban Service Routes',
        description: 'Optimized for suburban service calls with time windows',
        status: 'draft',
        rules: [
          {
            id: 'r3',
            type: 'priority',
            name: 'Priority Customers First',
            condition: 'customer.priority = high',
            action: 'order = first',
            enabled: true
          }
        ]
      }
    ];
    setChains(mockChains);
  }, []);

  const createNewChain = () => {
    const newChain: PlaybookChain = {
      id: Date.now().toString(),
      name: 'New Playbook Chain',
      description: 'Description for new playbook',
      status: 'draft',
      rules: []
    };
    setChains([...chains, newChain]);
    setSelectedChain(newChain);
    setIsEditing(true);
  };

  const addRule = () => {
    if (!selectedChain) return;
    
    const newRule: PlaybookRule = {
      id: Date.now().toString(),
      type: 'constraint',
      name: 'New Rule',
      condition: 'condition = value',
      action: 'action = value',
      enabled: true
    };

    const updatedChain = {
      ...selectedChain,
      rules: [...selectedChain.rules, newRule]
    };
    
    setSelectedChain(updatedChain);
    updateChainInList(updatedChain);
  };

  const updateChainInList = (updatedChain: PlaybookChain) => {
    setChains(chains.map(chain => 
      chain.id === updatedChain.id ? updatedChain : chain
    ));
  };

  const deleteRule = (ruleId: string) => {
    if (!selectedChain) return;
    
    const updatedChain = {
      ...selectedChain,
      rules: selectedChain.rules.filter(rule => rule.id !== ruleId)
    };
    
    setSelectedChain(updatedChain);
    updateChainInList(updatedChain);
  };

  const savePlaybook = async () => {
    if (!selectedChain) return;
    
    setSaving(true);
    try {
      // Call API to save playbook
      const response = await fetch('/api/playbook/save', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}`
        },
        body: JSON.stringify(selectedChain)
      });
      
      if (response.ok) {
        setIsEditing(false);
        // Update status to active if it was draft
        if (selectedChain.status === 'draft') {
          const activatedChain = { ...selectedChain, status: 'active' as const };
          setSelectedChain(activatedChain);
          updateChainInList(activatedChain);
        }
      }
    } catch (error) {
      console.error('Failed to save playbook:', error);
    } finally {
      setSaving(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-600 bg-green-50';
      case 'paused': return 'text-yellow-600 bg-yellow-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getRuleTypeColor = (type: string) => {
    switch (type) {
      case 'constraint': return 'text-red-600 bg-red-50';
      case 'optimization': return 'text-blue-600 bg-blue-50';
      case 'priority': return 'text-purple-600 bg-purple-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Playbook Editor</h1>
        <p className="text-gray-600 mt-2">Create and manage optimization rule chains</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chains List */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Playbook Chains</CardTitle>
                <Button 
                  onClick={createNewChain}
                  size="sm"
                  className="flex items-center gap-2"
                >
                  <Plus className="w-4 h-4" />
                  New
                </Button>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <div className="space-y-2">
                {chains.map((chain) => (
                  <div
                    key={chain.id}
                    onClick={() => setSelectedChain(chain)}
                    className={`p-4 cursor-pointer border-l-4 hover:bg-gray-50 transition-colors ${
                      selectedChain?.id === chain.id 
                        ? 'border-blue-500 bg-blue-50' 
                        : 'border-transparent'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-medium text-gray-900">{chain.name}</h3>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(chain.status)}`}>
                        {chain.status}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{chain.description}</p>
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>{chain.rules.length} rules</span>
                      {chain.successRate && (
                        <span className="text-green-600">{chain.successRate}% success</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Chain Editor */}
        <div className="lg:col-span-2">
          {selectedChain ? (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-xl">{selectedChain.name}</CardTitle>
                    <p className="text-gray-600 mt-1">{selectedChain.description}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      onClick={() => setIsEditing(!isEditing)}
                      variant="outline"
                      size="sm"
                    >
                      <Settings className="w-4 h-4 mr-2" />
                      {isEditing ? 'View' : 'Edit'}
                    </Button>
                    <Button
                      onClick={savePlaybook}
                      disabled={saving || !isEditing}
                      size="sm"
                      className="flex items-center gap-2"
                    >
                      <Save className="w-4 h-4" />
                      {saving ? 'Saving...' : 'Save'}
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {/* Rules Grid */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-medium">Rules</h3>
                    {isEditing && (
                      <Button onClick={addRule} size="sm" variant="outline">
                        <Plus className="w-4 h-4 mr-2" />
                        Add Rule
                      </Button>
                    )}
                  </div>

                  <div className="space-y-3">
                    {selectedChain.rules.map((rule, index) => (
                      <div key={rule.id} className="border rounded-lg p-4 bg-gray-50">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-medium text-gray-500">#{index + 1}</span>
                            <span className={`px-2 py-1 text-xs font-medium rounded ${getRuleTypeColor(rule.type)}`}>
                              {rule.type}
                            </span>
                            <h4 className="font-medium">{rule.name}</h4>
                          </div>
                          <div className="flex items-center gap-2">
                            {rule.enabled && <Check className="w-4 h-4 text-green-600" />}
                            {isEditing && (
                              <Button
                                onClick={() => deleteRule(rule.id)}
                                size="sm"
                                variant="outline"
                                className="text-red-600 hover:text-red-700"
                              >
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            )}
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                          <div>
                            <label className="block text-xs font-medium text-gray-500 mb-1">
                              CONDITION
                            </label>
                            <code className="block p-2 bg-white rounded text-xs font-mono">
                              {rule.condition}
                            </code>
                          </div>
                          <div className="flex items-center justify-center">
                            <ArrowRight className="w-4 h-4 text-gray-400" />
                          </div>
                          <div>
                            <label className="block text-xs font-medium text-gray-500 mb-1">
                              ACTION
                            </label>
                            <code className="block p-2 bg-white rounded text-xs font-mono">
                              {rule.action}
                            </code>
                          </div>
                        </div>
                      </div>
                    ))}

                    {selectedChain.rules.length === 0 && (
                      <div className="text-center py-8 text-gray-500">
                        <AlertTriangle className="w-8 h-8 mx-auto mb-2" />
                        <p>No rules defined</p>
                        <p className="text-sm">Add rules to build your optimization chain</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Execution Controls */}
                {selectedChain.status === 'active' && (
                  <div className="mt-6 pt-6 border-t">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium">Execution Status</h4>
                        <p className="text-sm text-gray-600">
                          Last run: {selectedChain.lastRun?.toLocaleString()}
                        </p>
                      </div>
                      <Button className="flex items-center gap-2">
                        <Play className="w-4 h-4" />
                        Run Now
                      </Button>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="py-12 text-center">
                <div className="text-gray-500">
                  <Settings className="w-12 h-12 mx-auto mb-4" />
                  <h3 className="text-lg font-medium mb-2">Select a Playbook Chain</h3>
                  <p>Choose a chain from the list to view and edit its rules</p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default PlaybookGUI;
