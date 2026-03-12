import React from 'react';
import ReactDOM from 'react-dom/client';
import { ConfigProvider, App as AntApp } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import { momentaLightTheme } from './theme';
import App from './App';
import { ErrorBoundary } from './components/ErrorBoundary';
import './styles/index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  // 注意：移除 React.StrictMode——StrictMode 在开发模式下会二次执行 effect，
  // 导致 Three.js/WebGL 上下文被重复初始化而崩溃（生产环境无此问题）。
  <ConfigProvider locale={zhCN} theme={momentaLightTheme}>
    <AntApp>
      <ErrorBoundary>
        <App />
      </ErrorBoundary>
    </AntApp>
  </ConfigProvider>
);
