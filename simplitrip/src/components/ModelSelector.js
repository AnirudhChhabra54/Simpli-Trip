import React, { useEffect, useState } from 'react';
import { getLlmModels, selectLlmModel } from '../services/aiService';
import { FaRobot, FaCircleNotch } from 'react-icons/fa';

const ModelSelector = () => {
  const [models, setModels] = useState([]);
  const [current, setCurrent] = useState('');
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const [switching, setSwitching] = useState(false);
  const [host, setHost] = useState('');

  useEffect(() => {
    const load = async () => {
      try {
        const data = await getLlmModels();
        setModels(data.models || []);
        setCurrent(data.current_model || '');
        setConnected(!!data.connected);
        setHost(data.host || '');
      } catch (err) {
        setConnected(false);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const handleSelect = async (model) => {
    if (!model || model === current) return;
    setSwitching(true);
    try {
      const data = await selectLlmModel(model);
      setCurrent(data.current_model);
    } catch (err) {
      console.error(err);
    } finally {
      setSwitching(false);
    }
  };

  return (
    <div className="flex items-center gap-2" title={host || 'LM Studio'}>
      <span className="relative flex h-2.5 w-2.5">
        {connected && (
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
        )}
        <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${connected ? 'bg-green-500' : 'bg-red-500'}`}></span>
      </span>
      <FaRobot className={`text-sm ${connected ? 'text-cyan-400' : 'text-gray-500'}`} />
      {loading ? (
        <span className="text-xs text-gray-400">Connecting to LM Studio…</span>
      ) : !connected || models.length === 0 ? (
        <span className="text-xs text-gray-400">LM Studio offline</span>
      ) : (
        <select
          value={current}
          onChange={(e) => handleSelect(e.target.value)}
          disabled={switching}
          className="max-w-[200px] bg-gray-700 border border-gray-600 text-gray-100 text-xs rounded-md px-2 py-1 focus:outline-none focus:border-cyan-500"
        >
          {models.map((m) => (
            <option key={m} value={m}>
              {m}
            </option>
          ))}
        </select>
      )}
      {switching && <FaCircleNotch className="text-cyan-400 animate-spin text-xs" />}
    </div>
  );
};

export default ModelSelector;