import React from 'react';
import { render, screen } from '@testing-library/react';
import App from '../App';

test('renders RouteForce Pro header', () => {
  render(<App />);
  const header = screen.getByText(/RouteForce Pro/i);
  expect(header).toBeInTheDocument();
});
