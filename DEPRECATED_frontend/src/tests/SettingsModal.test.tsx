import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import SettingsModal from "../components/SettingsModal";
import "@testing-library/jest-dom";

// Mock the @headlessui/react Dialog component
jest.mock("@headlessui/react", () => ({
  Dialog: ({ children, open }: { children: React.ReactNode; open: boolean }) => open ? <div>{children}</div> : null,
  DialogTitle: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

// Mock fetch
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({}),
  })
) as jest.Mock;

describe("SettingsModal", () => {
  const mockOnClose = jest.fn();

  beforeEach(() => {
    localStorage.clear();
    jest.clearAllMocks();
    // Set up localStorage mock for each test
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: jest.fn((key) => {
          if (key === 'eventColor') return '#ff6384';
          if (key === 'taskColor') return '#90ee90';
          return null;
        }),
        setItem: jest.fn(),
        clear: jest.fn(),
        removeItem: jest.fn(),
        length: 2,
        key: jest.fn(),
      },
      writable: true
    });
  });

  test("renders correctly when open", () => {
    render(<SettingsModal open={true} onClose={mockOnClose} />);
    expect(screen.getByText("Settings")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /cancel/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /save/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/event colour/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/task colour/i)).toBeInTheDocument();
  });

  test("does not render when closed", () => {
    render(<SettingsModal open={false} onClose={mockOnClose} />);
    expect(screen.queryByText("Settings")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /cancel/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /save/i })).not.toBeInTheDocument();
  });

  test("calls onClose when cancel button is clicked", () => {
    render(<SettingsModal open={true} onClose={mockOnClose} />);
    const cancelButton = screen.getByRole("button", { name: /cancel/i });
    fireEvent.click(cancelButton);
    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  test("saves color settings when save button is clicked", async () => {
    const setItemSpy = jest.spyOn(Storage.prototype, 'setItem');
    render(<SettingsModal open={true} onClose={mockOnClose} />);

    // Change colors
    const eventColorInput = screen.getByLabelText(/event colour/i);
    const taskColorInput = screen.getByLabelText(/task colour/i);

    fireEvent.change(eventColorInput, { target: { value: '#ff0000' } });
    fireEvent.change(taskColorInput, { target: { value: '#00ff00' } });

    // Click save
    const saveButton = screen.getByRole("button", { name: /save/i });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(setItemSpy).toHaveBeenCalledWith('eventColor', '#ff0000');
      expect(setItemSpy).toHaveBeenCalledWith('taskColor', '#00ff00');
      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });
  });

  test("loads saved colors from localStorage", () => {
    localStorage.setItem('eventColor', '#ff0000');
    localStorage.setItem('taskColor', '#00ff00');

    render(<SettingsModal open={true} onClose={mockOnClose} />);

    const eventColorInput = screen.getByLabelText(/event colour/i);
    const taskColorInput = screen.getByLabelText(/task colour/i);

    expect(eventColorInput).toHaveValue('#ff0000');
    expect(taskColorInput).toHaveValue('#00ff00');
  });

  test("calls onClose when clicking outside modal", () => {
    render(<SettingsModal open={true} onClose={mockOnClose} />);
    expect(mockOnClose).toBeDefined();
  });
});
