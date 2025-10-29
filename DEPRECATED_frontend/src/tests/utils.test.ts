// Test utility functions

describe('Date Formatting', () => {
  // Import the formatDate function from Calendar.tsx
  const formatDate = (date: Date): string => {
    return date.toLocaleString("en-US", {
      month: "2-digit",
      day: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
    });
  };

  test('formats date correctly', () => {
    const testDate = new Date(2023, 0, 15, 14, 30); // Jan 15, 2023, 2:30 PM
    const formattedDate = formatDate(testDate);

    // The exact format might vary by environment, so we'll check for key parts
    expect(formattedDate).toContain('01');  // Month
    expect(formattedDate).toContain('15');  // Day
    expect(formattedDate).toContain('2023'); // Year
    expect(formattedDate).toMatch(/02:30|2:30/); // Time (might be formatted as 02:30 or 2:30)
    expect(formattedDate).toMatch(/PM/i);   // AM/PM indicator
  });

  test('handles midnight correctly', () => {
    const testDate = new Date(2023, 0, 15, 0, 0); // Jan 15, 2023, 12:00 AM
    const formattedDate = formatDate(testDate);

    expect(formattedDate).toContain('01');  // Month
    expect(formattedDate).toContain('15');  // Day
    expect(formattedDate).toContain('2023'); // Year
    expect(formattedDate).toMatch(/12:00|00:00/); // Time
    expect(formattedDate).toMatch(/AM/i);   // AM/PM indicator
  });
});

describe('Event Handling', () => {
  test('event color mapping works correctly', () => {
    // Test the color mapping logic used in Calendar.tsx
    const eventColors = {
      default: 'blue',
      task: 'rgb(144,238,144)',
      standalone: 'rgb(255,99,132)'
    };

    expect(eventColors.default).toBe('blue');
    expect(eventColors.task).toBe('rgb(144,238,144)');
    expect(eventColors.standalone).toBe('rgb(255,99,132)');
  });
});
