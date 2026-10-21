import { StrictMode, useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import './style.css'

const API = 'http://localhost:8000/api'
type Post = { id: string; author_id: string; type: 'startup'|'vacancy'; title: string; description: string; looking_for: string }

function App() {
  const [token, setToken] = useState(localStorage.getItem('token') || '')
  const [posts, setPosts] = useState<Post[]>([])
  const [email, setEmail] = useState('founder@example.com')
  const [password, setPassword] = useState('password123')
  const [message, setMessage] = useState('')

  async function login() {
    const res = await fetch(`${API}/auth/login`, { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({email, password}) })
    if (!res.ok) return setMessage('Не удалось войти')
    const data = await res.json(); localStorage.setItem('token', data.access_token); setToken(data.access_token); setMessage('')
  }
  async function loadPosts() {
    const res = await fetch(`${API}/posts`, { headers: {Authorization: `Bearer ${token}`} })
    if (res.ok) setPosts(await res.json())
  }
  async function respond(postId: string) {
    const res = await fetch(`${API}/posts/${postId}/responses`, { method:'POST', headers:{Authorization:`Bearer ${token}`, 'Content-Type':'application/json'}, body:JSON.stringify({message:'Готов обсудить сотрудничество.'}) })
    setMessage(res.ok ? 'Отклик отправлен' : (await res.json()).detail)
  }
  useEffect(() => { if (token) loadPosts() }, [token])
  if (!token) return <main className="auth"><section className="card"><p className="eyebrow">STARTUP EXCHANGE</p><h1>Найдите свою команду</h1><p className="muted">Стартапы, вакансии и люди для совместных проектов.</p><input value={email} onChange={e=>setEmail(e.target.value)} placeholder="Email"/><input value={password} onChange={e=>setPassword(e.target.value)} type="password" placeholder="Пароль"/><button onClick={login}>Войти</button>{message && <p className="error">{message}</p>}</section></main>
  return <main><header><div><p className="eyebrow">STARTUP EXCHANGE</p><h1>Лента предложений</h1></div><button className="secondary" onClick={()=>{localStorage.removeItem('token');setToken('')}}>Выйти</button></header><section className="toolbar"><button>Все предложения</button><button className="secondary">Мои публикации</button><button className="secondary">Отклики</button></section>{message && <p className="notice">{message}</p>}<section className="grid">{posts.length ? posts.map(post=><article className="card" key={post.id}><span className="tag">{post.type === 'startup' ? 'Стартап' : 'Вакансия'}</span><h2>{post.title}</h2><p>{post.description}</p><p className="muted"><b>Ищет:</b> {post.looking_for}</p><button onClick={()=>respond(post.id)}>Откликнуться</button></article>) : <div className="empty"><h2>Пока нет предложений</h2><p className="muted">Когда появятся публикации, они будут показаны здесь.</p></div>}</section></main>
}

createRoot(document.getElementById('root')!).render(<StrictMode><App /></StrictMode>)
