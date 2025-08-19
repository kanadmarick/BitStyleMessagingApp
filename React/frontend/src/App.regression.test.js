import { render, screen, fireEvent } from '@testing-library/react';
import App from './App';

describe('BitStyleMessagingApp Regression', () => {
  test('renders login form', () => {
    render(<App />);
    expect(screen.getByPlaceholderText(/Username/i)).toBeInTheDocument();
    expect(screen.getByText(/Login/i)).toBeInTheDocument();
  });

  test('login and show chat UI', () => {
    render(<App />);
    fireEvent.change(screen.getByPlaceholderText(/Username/i), { target: { value: 'testuser' } });
    fireEvent.click(screen.getByText(/Login/i));
    expect(screen.getByPlaceholderText(/Type a message.../i)).toBeInTheDocument();
    expect(screen.getByText(/Send/i)).toBeInTheDocument();
  });

  test('cannot send message before secure connection', () => {
    render(<App />);
    fireEvent.change(screen.getByPlaceholderText(/Username/i), { target: { value: 'testuser' } });
    fireEvent.click(screen.getByText(/Login/i));
    fireEvent.change(screen.getByPlaceholderText(/Type a message.../i), { target: { value: 'Hello' } });
    fireEvent.click(screen.getByText(/Send/i));
    expect(screen.getByText(/Cannot send message: secure connection not yet established./i)).toBeInTheDocument();
  });
});
