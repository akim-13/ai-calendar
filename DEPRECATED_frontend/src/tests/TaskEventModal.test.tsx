import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import TaskEventModal from "../components/TaskEventModal";
import "@testing-library/jest-dom";

// Mock the @headlessui/react Dialog component
jest.mock("@headlessui/react", () => ({
  Dialog: ({ children, open }: { children: React.ReactNode; open: boolean }) => open ? <div>{children}</div> : null,
  DialogTitle: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

// Mock the TaskEventInputs components
jest.mock("../components/TaskEventInputs", () => ({
  TitleInput: ({ value, onChange }: any) => (
    <input data-testid="title-input" value={value} onChange={onChange} />
  ),
  StartDateInput: ({ value, onChange }: any) => (
    <input data-testid="start-date-input" value={value} onChange={onChange} />
  ),
  EndDateInput: ({ value, onChange }: any) => (
    <input data-testid="end-date-input" value={value} onChange={onChange} />
  ),
  DurationInput: ({ value, onChange }: any) => (
    <input data-testid="duration-input" value={value} onChange={onChange} />
  ),
  PrioritySelect: ({ value, onChange }: any) => (
    <select data-testid="priority-select" value={value} onChange={onChange}>
      <option value="1">Low Priority</option>
      <option value="2">Medium Priority</option>
      <option value="3">High Priority</option>
    </select>
  ),
  DescriptionInput: ({ value, onChange }: any) => (
    <textarea data-testid="description-input" value={value} onChange={onChange} />
  ),
  CompletedCheckbox: ({ checked, onChange }: any) => (
    <input type="checkbox" data-testid="completed-checkbox" checked={checked} onChange={onChange} />
  ),
  ModeToggleButton: ({ mode, isActive, setIsTaskMode }: any) => (
    <button data-testid={`${mode}-toggle`} onClick={() => setIsTaskMode(mode === "task")}>{mode}</button>
  ),
}));

// Mock axios
jest.mock("axios", () => ({
  put: jest.fn(() => Promise.resolve({ data: {} })),
  post: jest.fn(() => Promise.resolve({ data: {} })),
  delete: jest.fn(() => Promise.resolve({ data: {} })),
  get: jest.fn(() => Promise.resolve({ data: {} })),
}));

describe("TaskEventModal", () => {
  const defaultProps = {
    events: [],
    setEvents: jest.fn(),
    isModalOpen: true,
    setIsModalOpen: jest.fn(),
    newFCEvent: {
      current: {
        title: "",
        start: "",
        end: "",
        extendedProps: {
          description: "",
          duration: "",
          priority: "",
          isCompleted: false
        }
      }
    },
    initialExtendedProps: {
      description: "",
      duration: "",
      priority: "",
      isCompleted: false
    },
    isTaskMode: true,
    setIsTaskMode: jest.fn()
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders modal title for task mode", () => {
    render(<TaskEventModal {...defaultProps} />);
    expect(screen.getByText(/Manage Task/i)).toBeInTheDocument();
  });

  test("renders modal title for event mode", () => {
    render(<TaskEventModal {...defaultProps} modalType={false} />);
    expect(screen.getByText(/Manage Event/i)).toBeInTheDocument();
  });

  test("does not render when modal is closed", () => {
    render(<TaskEventModal {...defaultProps} isModalOpen={false} />);
    expect(screen.queryByText(/Manage Task/i)).not.toBeInTheDocument();
  });

  test("renders task mode inputs", () => {
    render(<TaskEventModal {...defaultProps} />);
    expect(screen.getByTestId("title-input")).toBeInTheDocument();
    expect(screen.getByTestId("start-date-input")).toBeInTheDocument();
    expect(screen.getByTestId("duration-input")).toBeInTheDocument();
    expect(screen.getByTestId("priority-select")).toBeInTheDocument();
    expect(screen.getByTestId("description-input")).toBeInTheDocument();
    expect(screen.getByTestId("completed-checkbox")).toBeInTheDocument();
  });

  test("renders event mode inputs", () => {
    render(<TaskEventModal {...defaultProps} modalType={false} />);
    expect(screen.getByTestId("title-input")).toBeInTheDocument();
    expect(screen.getByTestId("start-date-input")).toBeInTheDocument();
    expect(screen.getByTestId("end-date-input")).toBeInTheDocument();
    expect(screen.getByTestId("description-input")).toBeInTheDocument();
  });

  test("handles form submission for new event", async () => {
    const mockedPost = jest.fn().mockResolvedValueOnce({ data: {} });
    const mockedGet = jest.fn().mockResolvedValueOnce({
      data: {
        latest_task: {
          username: "testuser",
          taskID: "123"
        },
        latest_standalone_event: {
          username: "testuser",
          standaloneEventID: "456"
        }
      }
    });

    // Override the mock for this test
    const mockedAxios = require("axios");
    mockedAxios.post.mockImplementation(mockedPost);
    mockedAxios.get.mockImplementation(mockedGet);

    render(<TaskEventModal {...defaultProps} modalType={false} />);

    const titleInput = screen.getByTestId("title-input");
    const startInput = screen.getByTestId("start-date-input");
    const endInput = screen.getByTestId("end-date-input");

    fireEvent.change(titleInput, { target: { value: "New Event", name: "title" } });
    fireEvent.change(startInput, { target: { value: "2024-03-20T10:00", name: "start" } });
    fireEvent.change(endInput, { target: { value: "2024-03-20T11:00", name: "end" } });

    const form = screen.getByRole("form");
    await fireEvent.submit(form);

    await waitFor(() => {
      expect(mockedPost).toHaveBeenCalledWith(
        "http://localhost:8000/add_standalone_event",
        expect.any(FormData)
      );
      expect(mockedGet).toHaveBeenCalledWith(
        "http://localhost:8000/get_latest_standalone_event/joe"
      );
    });
  });
});
