import React from 'react';

type Density = 'comfortable' | 'compact';

export const DensityToggle: React.FC = () => {
  const [density, setDensity] = React.useState<Density>(() => {
    if (typeof document === 'undefined') return 'comfortable';
    return document.documentElement.classList.contains('density-compact') ? 'compact' : 'comfortable';
  });

  const toggle = () => {
    const next: Density = density === 'comfortable' ? 'compact' : 'comfortable';
    setDensity(next);
    const root = document.documentElement;
    if (next === 'compact') {
      root.classList.add('density-compact');
      localStorage.setItem('density', 'compact');
    } else {
      root.classList.remove('density-compact');
      localStorage.setItem('density', 'comfortable');
    }
  };

  React.useEffect(() => {
    const saved = localStorage.getItem('density') as Density | null;
    if (saved === 'compact') {
      document.documentElement.classList.add('density-compact');
      setDensity('compact');
    }
  }, []);

  return (
    <button
      onClick={toggle}
      aria-label="Toggle density"
      title="Toggle density"
      className="inline-flex items-center rounded-md border border-gray-300 dark:border-gray-700 px-3 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
    >
      <span className="mr-2">{density === 'compact' ? '🗜️' : '🧺'}</span>
      <span>{density === 'compact' ? 'Compact' : 'Comfortable'}</span>
    </button>
  );
};

export default DensityToggle;

