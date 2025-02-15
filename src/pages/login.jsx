import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import StarBorder from '../Rc_Animation/animations/StarBorder';
import '../styles/login.css';

const Login = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/api/v1/login', { // 更新 URL
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        setError(errorData.detail || '登录失败，请稍后重试');
        return;
      }

      const data = await response.json();
      localStorage.setItem('token', data.token);
      navigate('/stock-market');
      
    } catch (err) {
      console.error('Login error:', err);
      setError('登录失败，请稍后重试');
    }
};

  return (
    <div className="login-container">
      <div className="login-form-wrapper">
        <h2>登录</h2>
        {error && <div className="error-message">{error}</div>}
        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <input
              type="email"
              name="email"
              placeholder="电子邮箱"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <input
              type="password"
              name="password"
              placeholder="密码"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <StarBorder
              as="button"
              type="submit"
              color="cyan"
              speed="3s"
            >
              登录
            </StarBorder>
          </div>
        </form>
        <div className="form-footer">
          <p>还没有账号？ 
            <span 
              className="register-link"
              onClick={() => navigate('/register')}
            >
              立即注册
            </span>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;