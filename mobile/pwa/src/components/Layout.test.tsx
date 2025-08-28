import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Layout from './Layout';

// Mock child components
vi.mock('./Header', () => ({ default: () => <header data-testid="header" /> }));
vi.mock('./Navigation', () => ({ default: () => <nav data-testid="navigation" /> }));

// Mock Outlet to render children
vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    Outlet: () => <div data-testid="outlet">Outlet Content</div>,
  };
});

describe('Layout', () => {
  it('renders Header, Outlet, and Navigation', () => {
    render(
      <MemoryRouter>
        <Layout />
      </MemoryRouter>
    );
    expect(screen.getByTestId('header')).toBeInTheDocument();
    expect(screen.getByTestId('outlet')).toHaveTextContent('Outlet Content');
    expect(screen.getByTestId('navigation')).toBeInTheDocument();
  });

  it('applies correct layout classes', () => {
    render(
      <MemoryRouter>
        <Layout />
      </MemoryRouter>
    );
    const container = screen.getByRole('main').parentElement;
    expect(container).toHaveClass('min-h-screen', 'bg-gray-50', 'flex', 'flex-col');
  });
});
