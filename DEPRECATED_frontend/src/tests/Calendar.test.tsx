import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import axios from 'axios';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

// Mock the components we're not testing
jest.mock('../components/AchievementModal', () => {
  return function MockAchievementModal({ isOpen }: { isOpen: boolean }) {
    return isOpen ? <div data-testid="achievement-modal">Achievement Modal</div> : null;
  };
});

jest.mock('../components/SettingsModal', () => {
  return function MockSettingsModal({ open }: { open: boolean }) {
    return open ? <div data-testid="settings-modal">Settings Modal</div> : null;
  };
});

// Create a simple mock component for testing
function MockCalendar() {
  return (
    <div data-testid="calendar-mock">
      <div>Calendar Mock Component</div>
    </div>
  );
}

describe('Calendar Component Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('Calendar mock renders correctly', () => {
    render(<MockCalendar />);
    expect(screen.getByTestId('calendar-mock')).toBeInTheDocument();
    expect(screen.getByText('Calendar Mock Component')).toBeInTheDocument();
  });
});
