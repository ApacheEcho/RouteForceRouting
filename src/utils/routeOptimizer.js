// Simple nearest neighbor route optimization
export function optimizeRoute(locations) {
  if (!locations || locations.length < 2) return locations;
  const result = [locations[0]];
  const remaining = locations.slice(1);
  while (remaining.length) {
    const last = result[result.length - 1];
    let nearestIdx = 0;
    let nearestDist = distance(last, remaining[0]);
    for (let i = 1; i < remaining.length; i++) {
      const dist = distance(last, remaining[i]);
      if (dist < nearestDist) {
        nearestDist = dist;
        nearestIdx = i;
      }
    }
    result.push(remaining.splice(nearestIdx, 1)[0]);
  }
  return result;
}

function distance(a, b) {
  const dx = a.x - b.x;
  const dy = a.y - b.y;
  return Math.sqrt(dx * dx + dy * dy);
}

// Calculate ETA (simple: assume average speed 30 mph)
export function calculateETA(distanceMiles) {
  if (typeof distanceMiles !== 'number') return 'N/A';
  const hours = distanceMiles / 30;
  const minutes = Math.round(hours * 60);
  return `${minutes} min`;
}

// Simple fuel cost estimator (assume $3.5/gal and 8 mpg average)
export function calculateFuelCost(distanceMiles) {
  if (typeof distanceMiles !== 'number') return 'N/A';
  const gallons = distanceMiles / 8;
  const cost = (gallons * 3.5).toFixed(2);
  return cost;
}
