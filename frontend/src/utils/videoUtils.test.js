import { formatTimestamp, handleWatchClick } from './videoUtils';

describe('formatTimestamp', () => {
  test('converts decimal time to seconds correctly', () => {
    expect(formatTimestamp(15.3)).toBe(918); // 15 mins 18 secs
    expect(formatTimestamp(42.15)).toBe(2529); // 42 mins 9 secs
  });
});

describe('handleWatchClick', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
    global.window.open = jest.fn();
  });

  test('fetches video URL and opens in new window', async () => {
    const mockResponse = { url: 'https://youtube.com/watch?v=test' };
    global.fetch.mockResolvedValueOnce({
      json: () => Promise.resolve(mockResponse)
    });

    await handleWatchClick(15.3, 1);
    
    expect(global.fetch).toHaveBeenCalledWith('/api/video/1');
    expect(global.window.open).toHaveBeenCalledWith(
      'https://youtube.com/watch?v=test&t=918',
      '_blank'
    );
  });
}); 