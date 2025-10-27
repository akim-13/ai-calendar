import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import AchievementModal from '../components/AchievementModal';
import axios from 'axios';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('AchievementModal Component', () => {
  const mockOnClose = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();

    // Mock the window.matchMedia
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: jest.fn().mockImplementation((query: string) => ({
        matches: false, // Default to light mode
        media: query,
        onchange: null,
        addListener: jest.fn(),
        removeListener: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
      })),
    });

    // Mock API responses
    mockedAxios.get.mockImplementation((url: string) => {
      if (url.includes('check_achievements')) {
        return Promise.resolve({
          data: [
            {
              achievementID: 1,
              title: 'First Achievement',
              description: 'Complete your first task',
              requiredPoints: 10,
              image_path: 'achievement1.png',
            },
            {
              achievementID: 2,
              title: 'Second Achievement',
              description: 'Complete 5 tasks',
              requiredPoints: 50,
              image_path: 'achievement2.png',
            },
          ],
        });
      } else if (url.includes('get_user_points')) {
        return Promise.resolve({
          data: {
            points: 30,
          },
        });
      }
      return Promise.resolve({ data: {} });
    });
  });

  test('renders loading state initially when modal is open', () => {
    render(<AchievementModal isOpen={true} onClose={mockOnClose} />);
    expect(screen.getByText('Loading achievements...')).toBeInTheDocument();
  });

  test('does not render when isOpen is false', () => {
    render(<AchievementModal isOpen={false} onClose={mockOnClose} />);
    expect(screen.queryByText('Achievements')).not.toBeInTheDocument();
  });

  test('fetches and displays achievements when open', async () => {
    render(<AchievementModal isOpen={true} onClose={mockOnClose} />);

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByText('Loading achievements...')).not.toBeInTheDocument();
    });

    // Check API calls
    expect(mockedAxios.get).toHaveBeenCalledWith('http://localhost:8000/check_achievements');
    expect(mockedAxios.get).toHaveBeenCalledWith('http://localhost:8000/get_user_points/joe');

    // Check rendered content
    expect(screen.getByText('Achievements')).toBeInTheDocument();
    expect(screen.getByText('Your Points: 30')).toBeInTheDocument();

    // Use more flexible text matching for achievements
    expect(screen.getByText((content) => content.includes('First Achievement'))).toBeInTheDocument();
    expect(screen.getByText((content) => content.includes('Second Achievement'))).toBeInTheDocument();
  });

  test('filters achievements correctly', async () => {
    render(<AchievementModal isOpen={true} onClose={mockOnClose} />);

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByText('Loading achievements...')).not.toBeInTheDocument();
    });

    // Check initial state (all achievements visible)
    expect(screen.getByText((content) => content.includes('First Achievement'))).toBeInTheDocument();
    expect(screen.getByText((content) => content.includes('Second Achievement'))).toBeInTheDocument();

    // Click on "Completed" filter
    fireEvent.click(screen.getByText('Completed'));

    // First achievement should be visible (30 points > 10 required)
    expect(screen.getByText((content) => content.includes('First Achievement'))).toBeInTheDocument();

    // Click on "Locked" filter
    fireEvent.click(screen.getByText('Locked'));

    // Second achievement should be visible (30 points < 50 required)
    expect(screen.getByText((content) => content.includes('Second Achievement'))).toBeInTheDocument();
  });

  test('closes modal when close button is clicked', async () => {
    render(<AchievementModal isOpen={true} onClose={mockOnClose} />);

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByText('Loading achievements...')).not.toBeInTheDocument();
    });

    // Click the close button (✕)
    fireEvent.click(screen.getByText('✕'));

    // Check if onClose was called
    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });
});
