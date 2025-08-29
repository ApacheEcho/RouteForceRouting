import { render, screen, fireEvent } from '@testing-library/react';
import ProfilePage from './ProfilePage';
import * as useAuthModule from '../hooks/useAuth';

// Mock useAuth hook
const mockUser = {
  name: 'Jane Smith',
  role: 'Driver',
  email: 'jane@example.com',
  phone: '555-1234',
};

vi.mock('../hooks/useAuth', () => ({
  useAuth: () => ({ user: mockUser }),
}));

describe('ProfilePage', () => {
  it('renders profile header and user info', () => {
    render(<ProfilePage />);
    expect(screen.getByRole('main')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /profile/i })).toBeInTheDocument();
    expect(screen.getByText(/manage your account/i)).toBeInTheDocument();
    expect(screen.getByText(mockUser.name)).toBeInTheDocument();
    expect(screen.getByText(mockUser.role)).toBeInTheDocument();
    expect(screen.getByLabelText(/edit profile/i)).toBeInTheDocument();
  });

  it('renders profile stats', () => {
    render(<ProfilePage />);
    expect(screen.getByText(/routes completed/i)).toBeInTheDocument();
    expect(screen.getByText(/total distance/i)).toBeInTheDocument();
    expect(screen.getByText(/avg. efficiency/i)).toBeInTheDocument();
    expect(screen.getByText(/member since/i)).toBeInTheDocument();
    expect(screen.getByText('247')).toBeInTheDocument();
    expect(screen.getByText('15,432 km')).toBeInTheDocument();
    expect(screen.getByText('92%')).toBeInTheDocument();
    expect(screen.getByText('Jan 2023')).toBeInTheDocument();
  });

  it('renders contact info if present', () => {
    render(<ProfilePage />);
    // Use regex matcher for phone to handle possible formatting/splitting
    if (mockUser.email) {
      expect(screen.getByText((content) => content.includes(mockUser.email))).toBeInTheDocument();
    }
    if (mockUser.phone) {
      // Use function matcher to match phone number even if split across elements
      expect(screen.getByText((content, node) => {
        // Check if the node or any of its children contain the phone number
        const hasPhone = (n) => n && n.textContent && n.textContent.includes(mockUser.phone);
        return hasPhone(node) || Array.from(node?.childNodes || []).some(hasPhone);
      })).toBeInTheDocument();
    }
  });

  it('edit button is focusable and clickable', () => {
    render(<ProfilePage />);
    const editBtn = screen.getByLabelText(/edit profile/i);
    expect(editBtn).toHaveAttribute('tabindex', '0');
    fireEvent.click(editBtn);
    // No modal in this component, but button should be clickable
  });

  it('renders all regions with correct labels', () => {
  render(<ProfilePage />);
  expect(screen.getByRole('region', { name: /profile header/i })).toBeInTheDocument();
  expect(screen.getByRole('region', { name: /contact information/i })).toBeInTheDocument();
  expect(screen.getByRole('region', { name: /performance stats/i })).toBeInTheDocument();
  expect(screen.getByRole('region', { name: /recent activity/i })).toBeInTheDocument();
  });
});
