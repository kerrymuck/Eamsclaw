import request from './request'

export const authApi = {
  login: (username: string, password: string) =>
    request.post('/auth/login', { username, password }),
  
  getMe: () =>
    request.get('/auth/me')
}
