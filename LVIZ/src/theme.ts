import type { ThemeConfig } from 'antd';
import { theme } from 'antd';

// Momenta Light Theme
export const momentaLightTheme: ThemeConfig = {
  token: {
    // Brand Colors
    colorPrimary: '#0066FF',
    colorSuccess: '#00C853',
    colorWarning: '#FFB800',
    colorError: '#FF3B3B',
    colorInfo: '#0066FF',

    // Text Colors
    colorText: '#1A1A2E',
    colorTextSecondary: '#505F79',
    colorTextTertiary: '#6B778C',
    colorTextQuaternary: '#97A0AF',

    // Background Colors
    colorBgContainer: '#FFFFFF',
    colorBgElevated: '#FFFFFF',
    colorBgLayout: '#FAFBFC',
    colorBgSpotlight: 'rgba(26, 26, 46, 0.85)',
    colorBgMask: 'rgba(26, 26, 46, 0.45)',

    // Border Colors
    colorBorder: '#EBECF0',
    colorBorderSecondary: '#F4F5F7',

    // Link Colors
    colorLink: '#0066FF',
    colorLinkHover: '#3385FF',
    colorLinkActive: '#0052CC',

    // Typography
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif",
    fontFamilyCode: "'JetBrains Mono', 'SF Mono', Consolas, monospace",
    fontSize: 14,
    fontSizeHeading1: 36,
    fontSizeHeading2: 28,
    fontSizeHeading3: 22,
    fontSizeHeading4: 18,
    fontSizeHeading5: 16,

    // Border Radius
    borderRadius: 6,
    borderRadiusLG: 8,
    borderRadiusSM: 4,
    borderRadiusXS: 2,

    // Shadows
    boxShadow: '0 1px 3px 0 rgba(26, 26, 46, 0.1), 0 1px 2px -1px rgba(26, 26, 46, 0.06)',
    boxShadowSecondary: '0 4px 6px -1px rgba(26, 26, 46, 0.1), 0 2px 4px -2px rgba(26, 26, 46, 0.06)',

    // Spacing
    padding: 16,
    paddingLG: 24,
    paddingSM: 12,
    paddingXS: 8,
    margin: 16,
    marginLG: 24,
    marginSM: 12,
    marginXS: 8,

    // Motion
    motionDurationFast: '0.1s',
    motionDurationMid: '0.2s',
    motionDurationSlow: '0.3s',
  },
  components: {
    Button: {
      colorPrimary: '#0066FF',
      algorithm: true,
      primaryShadow: '0 2px 4px rgba(0, 102, 255, 0.2)',
      fontWeight: 600,
    },
    Card: {
      headerBg: '#FAFBFC',
      colorBorderSecondary: '#EBECF0',
    },
    Table: {
      headerBg: '#FAFBFC',
      headerColor: '#1A1A2E',
      rowHoverBg: '#F4F5F7',
      borderColor: '#EBECF0',
    },
    Menu: {
      itemBg: 'transparent',
      itemSelectedBg: '#E6F0FF',
      itemSelectedColor: '#0066FF',
      itemHoverBg: '#F4F5F7',
    },
    Input: {
      colorBorder: '#EBECF0',
      hoverBorderColor: '#0066FF',
      activeBorderColor: '#0066FF',
    },
    Select: {
      colorBorder: '#EBECF0',
      optionSelectedBg: '#E6F0FF',
    },
    Tag: {
      colorFillSecondary: '#E6F0FF',
    },
    Badge: {
      colorBgContainer: '#FF3B3B',
    },
    Statistic: {
      titleFontSize: 14,
      contentFontSize: 28,
    },
  },
};

// Momenta Dark Theme
export const momentaDarkTheme: ThemeConfig = {
  algorithm: theme.darkAlgorithm,
  token: {
    // Brand Colors (adjusted for dark mode)
    colorPrimary: '#3385FF',
    colorSuccess: '#00E676',
    colorWarning: '#FFD54F',
    colorError: '#FF5252',
    colorInfo: '#3385FF',

    // Text Colors
    colorText: 'rgba(255, 255, 255, 0.87)',
    colorTextSecondary: 'rgba(255, 255, 255, 0.65)',
    colorTextTertiary: 'rgba(255, 255, 255, 0.45)',
    colorTextQuaternary: 'rgba(255, 255, 255, 0.25)',

    // Background Colors
    colorBgContainer: '#1A1A2E',
    colorBgElevated: '#16213E',
    colorBgLayout: '#0F0F1A',
    colorBgSpotlight: 'rgba(255, 255, 255, 0.85)',
    colorBgMask: 'rgba(0, 0, 0, 0.65)',

    // Border Colors
    colorBorder: '#2D3548',
    colorBorderSecondary: '#252A3D',

    // Typography
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif",
    fontFamilyCode: "'JetBrains Mono', 'SF Mono', Consolas, monospace",
    fontSize: 14,

    // Border Radius
    borderRadius: 6,
    borderRadiusLG: 8,
    borderRadiusSM: 4,

    // Shadows
    boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.3), 0 1px 2px -1px rgba(0, 0, 0, 0.2)',
    boxShadowSecondary: '0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -2px rgba(0, 0, 0, 0.3)',
  },
  components: {
    Button: {
      colorPrimary: '#3385FF',
      algorithm: true,
      primaryShadow: '0 2px 8px rgba(51, 133, 255, 0.35)',
    },
    Card: {
      headerBg: '#16213E',
      colorBorderSecondary: '#2D3548',
    },
    Table: {
      headerBg: '#16213E',
      headerColor: 'rgba(255, 255, 255, 0.87)',
      rowHoverBg: '#252A3D',
      borderColor: '#2D3548',
    },
    Menu: {
      itemBg: '#1A1A2E',
      subMenuItemBg: '#0F0F1A',
      itemSelectedBg: 'rgba(51, 133, 255, 0.2)',
      itemSelectedColor: '#3385FF',
      itemHoverBg: '#252A3D',
    },
    Input: {
      colorBgContainer: '#16213E',
      colorBorder: '#2D3548',
    },
    Select: {
      colorBgContainer: '#16213E',
      colorBgElevated: '#1A1A2E',
      optionSelectedBg: 'rgba(51, 133, 255, 0.2)',
    },
  },
};

// Chart color palette
export const momentaChartColors = {
  primary: ['#0066FF', '#3385FF', '#66A3FF', '#99C2FF', '#CCE0FF'],
  status: {
    success: '#00C853',
    warning: '#FFB800',
    error: '#FF3B3B',
    info: '#0066FF',
  },
  categorical: [
    '#0066FF', // Momenta Blue
    '#00C853', // Success Green
    '#7C4DFF', // Tech Purple
    '#00BCD4', // Cyan
    '#FF6F00', // Orange
    '#E91E63', // Pink
    '#FFB800', // Warning Yellow
    '#607D8B', // Blue Gray
  ],
};
