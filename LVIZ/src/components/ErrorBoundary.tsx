import React from 'react';
import { Typography } from 'antd';

const { Text } = Typography;

interface State {
  hasError: boolean;
  message: string;
}

interface Props {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

/**
 * 全局错误边界——防止子树崩溃导致整页变白。
 */
export class ErrorBoundary extends React.Component<Props, State> {
  state: State = { hasError: false, message: '' };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, message: error?.message ?? '未知错误' };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error('[ErrorBoundary] 渲染出错:', error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback ?? (
          <div
            style={{
              width: '100%',
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 8,
              background: '#F5F5F5',
              padding: 16,
            }}
          >
            <Text type="secondary" style={{ fontSize: 12, textAlign: 'center' }}>
              渲染出错，请刷新页面
            </Text>
            <Text type="secondary" style={{ fontSize: 10, color: '#AAA' }}>
              {this.state.message}
            </Text>
          </div>
        )
      );
    }
    return this.props.children;
  }
}
