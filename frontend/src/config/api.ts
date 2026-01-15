// API Configuration
// When served from the same origin (backend serves frontend), use empty string
// When using separate servers, specify the full URL

// For production/ngrok (frontend served by backend):
export const API_BASE_URL = '';

// For local development with separate servers:
// export const API_BASE_URL = 'http://localhost:8000';

// For ngrok with separate tunnels (not recommended for free tier):
// export const API_BASE_URL = 'https://cannon-nonadoptable-hypocritically.ngrok-free.dev';

// Helper to construct API endpoints
export const api = {
    status: () => `${API_BASE_URL}/api/status`,
    videos: () => `${API_BASE_URL}/api/videos`,
    generate: () => `${API_BASE_URL}/api/generate`,
    storyCharacters: () => `${API_BASE_URL}/api/story/characters`,
    storyGenerate: () => `${API_BASE_URL}/api/story/generate`,
    storyStatus: (storyId: string) => `${API_BASE_URL}/api/story/${storyId}/status`,
    videoFile: (filename: string) => `${API_BASE_URL}/data/videos/${filename}`,
};
