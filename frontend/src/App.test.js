import { render, screen } from '@testing-library/react';
import App from './App';
import ToxicityBadge from './components/ToxicityBadge';

// Plain functions, not jest.fn(): Create React App resets jest.fn() mocks before every test.
jest.mock('./api', () => ({
  auth: {
    csrf: () => Promise.resolve(),
    me: () => Promise.reject(new Error('signed out')),
  },
  chat: {},
  moderation: {},
  feedback: {},
  errorMessage: () => 'error',
  mediaUrl: () => null,
}));

test('shows the sign-in form when nobody is signed in', async () => {
  render(<App />);
  expect(await screen.findByRole('heading', { name: 'Sign in' })).toBeInTheDocument();
  expect(screen.getByLabelText('Username')).toBeInTheDocument();
});

test('flagged messages get a label with the confidence', () => {
  render(<ToxicityBadge label="insult" score={0.83} />);
  expect(screen.getByText(/insult/)).toHaveTextContent('insult · 83%');
});

test('clean messages get no badge', () => {
  const { container } = render(<ToxicityBadge label="non-toxic" score={0.9} />);
  expect(container).toBeEmptyDOMElement();
});
