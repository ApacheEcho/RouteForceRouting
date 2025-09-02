import React, { useState } from 'react';

const vehicleTypes = [
  { type: 'Car', commercial: false },
  { type: 'Van', commercial: false },
  { type: 'Truck', commercial: true },
  { type: 'Commercial Truck', commercial: true },
];

function VehicleSelector() {
  const [selected, setSelected] = useState(vehicleTypes[0].type);

  return (
    <div>
      <h2>Select Vehicle Type</h2>
      <select value={selected} onChange={e => setSelected(e.target.value)}>
        {vehicleTypes.map(v => (
          <option key={v.type} value={v.type}>{v.type}</option>
        ))}
      </select>
      <p>
        {vehicleTypes.find(v => v.type === selected).commercial
          ? 'Commercial routing enabled: Avoid restricted areas.'
          : 'Standard routing.'}
      </p>
    </div>
  );
}

export default VehicleSelector;
