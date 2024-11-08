
const AUTH_BASE_URL = '/auth'

export const login = async (credentials) => {
  const response = await fetch(`${AUTH_BASE_URL}/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(credentials)
  });
  if (!response.ok) throw new Error('Login failed')
    return response.json();
}