import { render, screen, fireEvent } from "@testing-library/react";
import InputPrompt from "../components/InputPrompt";
import "@testing-library/jest-dom";

// Mock lucide-react icons
jest.mock("lucide-react", () => ({
  Check: () => <div data-testid="check-icon">Check</div>,
  Plus: () => <div data-testid="plus-icon">Plus</div>,
}));

describe("InputPrompt", () => {
  const mockSetIsModalOpen = jest.fn();
  const mockSetIsTaskMode = jest.fn();
  const mockNewFCEvent = { current: null };
  const mockInitialExtendedProps = {};

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders input field and buttons", () => {
    render(
      <InputPrompt
        setIsModalOpen={mockSetIsModalOpen}
        newFCEvent={mockNewFCEvent}
        initialExtendedProps={mockInitialExtendedProps}
        setModalType={mockSetIsTaskMode}
      />
    );

    // Check if input field is rendered
    expect(screen.getByPlaceholderText("Type your prompt...")).toBeInTheDocument();

    // Check if both buttons are rendered
    expect(screen.getByTestId("check-icon")).toBeInTheDocument();
    expect(screen.getByTestId("plus-icon")).toBeInTheDocument();
  });

  test("handles input change", () => {
    render(
      <InputPrompt
        setIsModalOpen={mockSetIsModalOpen}
        newFCEvent={mockNewFCEvent}
        initialExtendedProps={mockInitialExtendedProps}
        setModalType={mockSetIsTaskMode}
      />
    );

    const input = screen.getByPlaceholderText("Type your prompt...");
    fireEvent.change(input, { target: { value: "test input" } });
    expect(input).toHaveValue("test input");
  });

  test("opens modal when plus button is clicked", () => {
    render(
      <InputPrompt
        setIsModalOpen={mockSetIsModalOpen}
        newFCEvent={mockNewFCEvent}
        initialExtendedProps={mockInitialExtendedProps}
        setModalType={mockSetIsTaskMode}
      />
    );

    const plusButton = screen.getByTestId("plus-icon").parentElement;
    fireEvent.click(plusButton!);
    expect(mockSetIsModalOpen).toHaveBeenCalledWith(true);
  });
});
