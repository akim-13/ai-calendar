# Testing Guide

This directory contains tests for the frontend components using Jest and React Testing Library.

## Setup

Before running the tests, you need to install the required dependencies:

```bash
npm install --legacy-peer-deps
```

## Running Tests

To run all tests:

```bash
npm test
```

To run tests in watch mode (tests will automatically re-run when files change):

```bash
npm run test:watch
```

To run a specific test file:

```bash
npm test -- Calendar.test.tsx
```

## Test Files

- `Calendar.test.tsx`: Tests for the Calendar component
- `AchievementModal.test.tsx`: Tests for the AchievementModal component
- `utils.test.ts`: Tests for utility functions
- `setup.ts`: Setup file for Jest configuration

## Mocks

The tests use several mocks:

1. **API Mocks**: All API calls are mocked using Jest's mock functionality for axios
2. **Component Mocks**: Child components are mocked to simplify testing
3. **Browser API Mocks**: Browser APIs like `matchMedia` and `ResizeObserver` are mocked in the setup file

## Test Coverage

The tests cover the following functionality:

### Calendar Component
- Basic rendering of the component
- Note: We use a simplified mock for the Calendar component to avoid issues with FullCalendar

### AchievementModal Component
- Rendering loading state
- Not rendering when closed
- Fetching and displaying achievements
- Filtering achievements
- Closing the modal when the close button is clicked

### Utility Functions
- Date formatting
- Event color mapping

## Known Issues

There are some warnings about React updates not being wrapped in act(), but these are just warnings and don't affect the test results. These warnings are related to asynchronous state updates in the AchievementModal component.

## Troubleshooting

If you encounter issues with the tests:

1. Make sure all dependencies are installed with `npm install --legacy-peer-deps`
2. Check that the Jest configuration in `jest.config.js` is correct
3. Ensure that the TypeScript configuration in `tsconfig.jest.json` is correct
4. If you see errors related to ESM modules, check that the `type` field in `package.json` is set to `commonjs`
