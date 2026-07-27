import React, { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const stored = localStorage.getItem('omega_erp_user')
    if (stored) {
      try { setUser(JSON.parse(stored)) } catch {}
    }
    setIsLoading(false)
  }, [])

  const login = async (username, password) => {
    // Replace with real API call: await api.post('/auth/login/', { username, password })
    if (!username || !password) throw new Error('Invalid credentials')
    const mockUser = {
      id: 1,
      username,
      fullName: 'Rajesh Kumar',
      role: 'Procurement Manager',
      email: `${username}@omega-erp.com`,
      permissions: ['view_all', 'create_po', 'approve_payment'],
    }
    setUser(mockUser)
    localStorage.setItem('omega_erp_user', JSON.stringify(mockUser))
    return mockUser
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem('omega_erp_user')
  }

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, isLoading, login, logout }}>
      {!isLoading && children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
