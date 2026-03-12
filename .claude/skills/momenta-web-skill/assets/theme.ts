/**
 * Momenta UI Theme Configuration for Ant Design 5.x
 *
 * This file provides complete theme configuration for Momenta-branded
 * React applications using Ant Design.
 *
 * Usage:
 * ```tsx
 * import { ConfigProvider, App } from 'antd';
 * import { momentaLightTheme, momentaDarkTheme } from './theme';
 *
 * const MyApp = () => (
 *   <ConfigProvider theme={momentaLightTheme}>
 *     <App>
 *       {children}
 *     </App>
 *   </ConfigProvider>
 * );
 * ```
 */

import { theme } from 'antd';
import type { ThemeConfig } from 'antd';

// =============================================================================
// COLOR DEFINITIONS
// =============================================================================

export const momentaColors = {
  // Primary Brand Colors
  primary: {
    50: '#E6F0FF',
    100: '#CCE0FF',
    200: '#99C2FF',
    300: '#66A3FF',
    400: '#3385FF',
    500: '#0066FF', // Main brand color
    600: '#0052CC',
    700: '#003D99',
    800: '#002966',
    900: '#001433',
  },

  // Tech Black (Neutrals)
  neutral: {
    50: '#FAFBFC',
    100: '#F4F5F7',
    200: '#EBECF0',
    300: '#DFE1E6',
    400: '#C1C7D0',
    500: '#97A0AF',
    600: '#6B778C',
    700: '#505F79',
    800: '#344563',
    900: '#1A1A2E', // Tech Black
    950: '#0F0F1A',
  },

  // Functional Colors
  success: {
    light: '#E8F9EE',
    main: '#00C853',
    dark: '#00A846',
  },
  warning: {
    light: '#FFF8E6',
    main: '#FFB800',
    dark: '#E6A600',
  },
  error: {
    light: '#FFEBEB',
    main: '#FF3B3B',
    dark: '#E62E2E',
  },
  info: {
    light: '#E6F0FF',
    main: '#0066FF',
    dark: '#0052CC',
  },
} as const;

// =============================================================================
// LIGHT THEME
// =============================================================================

export const momentaLightTheme: ThemeConfig = {
  token: {
    // Brand Colors
    colorPrimary: momentaColors.primary[500],
    colorSuccess: momentaColors.success.main,
    colorWarning: momentaColors.warning.main,
    colorError: momentaColors.error.main,
    colorInfo: momentaColors.info.main,

    // Text Colors
    colorText: momentaColors.neutral[900],
    colorTextSecondary: momentaColors.neutral[700],
    colorTextTertiary: momentaColors.neutral[600],
    colorTextQuaternary: momentaColors.neutral[500],

    // Background Colors
    colorBgContainer: '#FFFFFF',
    colorBgElevated: '#FFFFFF',
    colorBgLayout: momentaColors.neutral[50],
    colorBgSpotlight: 'rgba(26, 26, 46, 0.85)',
    colorBgMask: 'rgba(26, 26, 46, 0.45)',

    // Border Colors
    colorBorder: momentaColors.neutral[200],
    colorBorderSecondary: momentaColors.neutral[100],

    // Link Colors
    colorLink: momentaColors.primary[500],
    colorLinkHover: momentaColors.primary[400],
    colorLinkActive: momentaColors.primary[600],

    // Fill Colors
    colorFill: 'rgba(26, 26, 46, 0.15)',
    colorFillSecondary: 'rgba(26, 26, 46, 0.06)',
    colorFillTertiary: 'rgba(26, 26, 46, 0.04)',
    colorFillQuaternary: 'rgba(26, 26, 46, 0.02)',

    // Typography
    fontFamily:
      "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif",
    fontFamilyCode: "'JetBrains Mono', 'SF Mono', Consolas, monospace",
    fontSize: 14,
    fontSizeSM: 12,
    fontSizeLG: 16,
    fontSizeXL: 20,
    fontSizeHeading1: 36,
    fontSizeHeading2: 28,
    fontSizeHeading3: 22,
    fontSizeHeading4: 18,
    fontSizeHeading5: 16,
    lineHeight: 1.5714285714,
    lineHeightSM: 1.6666666667,
    lineHeightLG: 1.5,
    lineHeightHeading1: 1.2222222222,
    lineHeightHeading2: 1.2857142857,
    lineHeightHeading3: 1.3636363636,
    lineHeightHeading4: 1.4444444444,
    lineHeightHeading5: 1.5,
    fontWeightStrong: 600,

    // Border Radius
    borderRadius: 6,
    borderRadiusLG: 8,
    borderRadiusSM: 4,
    borderRadiusXS: 2,

    // Shadows
    boxShadow:
      '0 1px 3px 0 rgba(26, 26, 46, 0.1), 0 1px 2px -1px rgba(26, 26, 46, 0.06)',
    boxShadowSecondary:
      '0 4px 6px -1px rgba(26, 26, 46, 0.1), 0 2px 4px -2px rgba(26, 26, 46, 0.06)',

    // Spacing
    padding: 16,
    paddingLG: 24,
    paddingMD: 20,
    paddingSM: 12,
    paddingXS: 8,
    paddingXXS: 4,
    margin: 16,
    marginLG: 24,
    marginMD: 20,
    marginSM: 12,
    marginXS: 8,
    marginXXS: 4,

    // Sizes
    controlHeight: 32,
    controlHeightLG: 40,
    controlHeightSM: 24,

    // Motion
    motionDurationFast: '0.1s',
    motionDurationMid: '0.2s',
    motionDurationSlow: '0.3s',
    motionEaseInOut: 'cubic-bezier(0.645, 0.045, 0.355, 1)',
    motionEaseOut: 'cubic-bezier(0.215, 0.61, 0.355, 1)',
    motionEaseIn: 'cubic-bezier(0.55, 0.055, 0.675, 0.19)',
  },

  components: {
    // Button
    Button: {
      colorPrimary: momentaColors.primary[500],
      algorithm: true,
      primaryShadow: '0 2px 4px rgba(0, 102, 255, 0.2)',
      fontWeight: 600,
      defaultBorderColor: momentaColors.neutral[200],
      defaultColor: momentaColors.neutral[700],
    },

    // Card
    Card: {
      headerBg: momentaColors.neutral[50],
      colorBorderSecondary: momentaColors.neutral[200],
      paddingLG: 24,
    },

    // Table
    Table: {
      headerBg: momentaColors.neutral[50],
      headerColor: momentaColors.neutral[900],
      rowHoverBg: momentaColors.neutral[100],
      borderColor: momentaColors.neutral[200],
      headerSplitColor: momentaColors.neutral[200],
      cellPaddingBlock: 12,
      cellPaddingInline: 16,
    },

    // Menu
    Menu: {
      itemBg: 'transparent',
      itemSelectedBg: momentaColors.primary[50],
      itemSelectedColor: momentaColors.primary[500],
      itemHoverBg: momentaColors.neutral[100],
      itemHoverColor: momentaColors.neutral[900],
      subMenuItemBg: 'transparent',
    },

    // Input
    Input: {
      colorBorder: momentaColors.neutral[200],
      hoverBorderColor: momentaColors.primary[500],
      activeBorderColor: momentaColors.primary[500],
      activeShadow: `0 0 0 2px ${momentaColors.primary[50]}`,
    },

    // Select
    Select: {
      colorBorder: momentaColors.neutral[200],
      optionSelectedBg: momentaColors.primary[50],
      optionSelectedColor: momentaColors.primary[500],
    },

    // DatePicker
    DatePicker: {
      colorBorder: momentaColors.neutral[200],
      activeBorderColor: momentaColors.primary[500],
    },

    // Tag
    Tag: {
      colorFillSecondary: momentaColors.primary[50],
      defaultBg: momentaColors.neutral[100],
    },

    // Badge
    Badge: {
      colorBgContainer: momentaColors.error.main,
    },

    // Statistic
    Statistic: {
      titleFontSize: 14,
      contentFontSize: 28,
    },

    // Modal
    Modal: {
      headerBg: '#FFFFFF',
      contentBg: '#FFFFFF',
      footerBg: '#FFFFFF',
      titleFontSize: 18,
    },

    // Drawer
    Drawer: {
      colorBgElevated: '#FFFFFF',
    },

    // Tabs
    Tabs: {
      itemColor: momentaColors.neutral[600],
      itemSelectedColor: momentaColors.primary[500],
      itemHoverColor: momentaColors.primary[400],
      inkBarColor: momentaColors.primary[500],
    },

    // Steps
    Steps: {
      colorPrimary: momentaColors.primary[500],
    },

    // Progress
    Progress: {
      defaultColor: momentaColors.primary[500],
      remainingColor: momentaColors.neutral[200],
    },

    // Alert
    Alert: {
      colorSuccessBg: momentaColors.success.light,
      colorSuccessBorder: momentaColors.success.main,
      colorWarningBg: momentaColors.warning.light,
      colorWarningBorder: momentaColors.warning.main,
      colorErrorBg: momentaColors.error.light,
      colorErrorBorder: momentaColors.error.main,
      colorInfoBg: momentaColors.info.light,
      colorInfoBorder: momentaColors.info.main,
    },

    // Notification
    Notification: {
      colorBgElevated: '#FFFFFF',
    },

    // Tooltip
    Tooltip: {
      colorBgSpotlight: momentaColors.neutral[900],
      colorTextLightSolid: '#FFFFFF',
    },

    // Popover
    Popover: {
      colorBgElevated: '#FFFFFF',
    },

    // Breadcrumb
    Breadcrumb: {
      itemColor: momentaColors.neutral[600],
      lastItemColor: momentaColors.neutral[900],
      linkColor: momentaColors.neutral[600],
      linkHoverColor: momentaColors.primary[500],
      separatorColor: momentaColors.neutral[400],
    },

    // Pagination
    Pagination: {
      itemActiveBg: momentaColors.primary[500],
      itemActiveColorDisabled: momentaColors.neutral[400],
    },

    // Checkbox
    Checkbox: {
      colorPrimary: momentaColors.primary[500],
    },

    // Radio
    Radio: {
      colorPrimary: momentaColors.primary[500],
    },

    // Switch
    Switch: {
      colorPrimary: momentaColors.primary[500],
    },

    // Slider
    Slider: {
      colorPrimary: momentaColors.primary[500],
      colorPrimaryBorder: momentaColors.primary[400],
      colorPrimaryBorderHover: momentaColors.primary[300],
    },

    // Form
    Form: {
      labelColor: momentaColors.neutral[900],
      labelRequiredMarkColor: momentaColors.error.main,
    },

    // Divider
    Divider: {
      colorSplit: momentaColors.neutral[200],
    },

    // Typography
    Typography: {
      colorText: momentaColors.neutral[900],
      colorTextSecondary: momentaColors.neutral[700],
      colorLink: momentaColors.primary[500],
      colorLinkHover: momentaColors.primary[400],
      colorLinkActive: momentaColors.primary[600],
    },
  },
};

// =============================================================================
// DARK THEME
// =============================================================================

export const momentaDarkTheme: ThemeConfig = {
  algorithm: theme.darkAlgorithm,

  token: {
    // Brand Colors (adjusted for dark mode)
    colorPrimary: momentaColors.primary[400], // Brighter for dark bg
    colorSuccess: '#00E676',
    colorWarning: '#FFD54F',
    colorError: '#FF5252',
    colorInfo: momentaColors.primary[400],

    // Text Colors
    colorText: 'rgba(255, 255, 255, 0.87)',
    colorTextSecondary: 'rgba(255, 255, 255, 0.65)',
    colorTextTertiary: 'rgba(255, 255, 255, 0.45)',
    colorTextQuaternary: 'rgba(255, 255, 255, 0.25)',

    // Background Colors
    colorBgContainer: momentaColors.neutral[900],
    colorBgElevated: '#16213E',
    colorBgLayout: momentaColors.neutral[950],
    colorBgSpotlight: 'rgba(255, 255, 255, 0.85)',
    colorBgMask: 'rgba(0, 0, 0, 0.65)',

    // Border Colors
    colorBorder: '#2D3548',
    colorBorderSecondary: '#252A3D',

    // Link Colors
    colorLink: momentaColors.primary[400],
    colorLinkHover: momentaColors.primary[300],
    colorLinkActive: momentaColors.primary[500],

    // Fill Colors
    colorFill: 'rgba(255, 255, 255, 0.18)',
    colorFillSecondary: 'rgba(255, 255, 255, 0.12)',
    colorFillTertiary: 'rgba(255, 255, 255, 0.08)',
    colorFillQuaternary: 'rgba(255, 255, 255, 0.04)',

    // Typography
    fontFamily:
      "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif",
    fontFamilyCode: "'JetBrains Mono', 'SF Mono', Consolas, monospace",
    fontSize: 14,
    fontSizeSM: 12,
    fontSizeLG: 16,
    fontSizeXL: 20,
    fontSizeHeading1: 36,
    fontSizeHeading2: 28,
    fontSizeHeading3: 22,
    fontSizeHeading4: 18,
    fontSizeHeading5: 16,
    fontWeightStrong: 600,

    // Border Radius
    borderRadius: 6,
    borderRadiusLG: 8,
    borderRadiusSM: 4,
    borderRadiusXS: 2,

    // Shadows
    boxShadow:
      '0 1px 3px 0 rgba(0, 0, 0, 0.3), 0 1px 2px -1px rgba(0, 0, 0, 0.2)',
    boxShadowSecondary:
      '0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -2px rgba(0, 0, 0, 0.3)',

    // Spacing
    padding: 16,
    paddingLG: 24,
    paddingMD: 20,
    paddingSM: 12,
    paddingXS: 8,
    margin: 16,
    marginLG: 24,
    marginMD: 20,
    marginSM: 12,
    marginXS: 8,

    // Motion
    motionDurationFast: '0.1s',
    motionDurationMid: '0.2s',
    motionDurationSlow: '0.3s',
  },

  components: {
    // Button
    Button: {
      colorPrimary: momentaColors.primary[400],
      algorithm: true,
      primaryShadow: '0 2px 8px rgba(51, 133, 255, 0.35)',
      fontWeight: 600,
      defaultBorderColor: '#2D3548',
      defaultColor: 'rgba(255, 255, 255, 0.65)',
    },

    // Card
    Card: {
      headerBg: '#16213E',
      colorBorderSecondary: '#2D3548',
      colorBgContainer: momentaColors.neutral[900],
    },

    // Table
    Table: {
      headerBg: '#16213E',
      headerColor: 'rgba(255, 255, 255, 0.87)',
      rowHoverBg: '#252A3D',
      borderColor: '#2D3548',
      headerSplitColor: '#2D3548',
      colorBgContainer: momentaColors.neutral[900],
    },

    // Menu
    Menu: {
      itemBg: momentaColors.neutral[900],
      subMenuItemBg: momentaColors.neutral[950],
      itemSelectedBg: 'rgba(51, 133, 255, 0.2)',
      itemSelectedColor: momentaColors.primary[400],
      itemHoverBg: '#252A3D',
      itemHoverColor: 'rgba(255, 255, 255, 0.87)',
    },

    // Input
    Input: {
      colorBgContainer: '#16213E',
      colorBorder: '#2D3548',
      hoverBorderColor: momentaColors.primary[400],
      activeBorderColor: momentaColors.primary[400],
      activeShadow: '0 0 0 2px rgba(51, 133, 255, 0.2)',
    },

    // Select
    Select: {
      colorBgContainer: '#16213E',
      colorBgElevated: momentaColors.neutral[900],
      optionSelectedBg: 'rgba(51, 133, 255, 0.2)',
      optionSelectedColor: momentaColors.primary[400],
    },

    // DatePicker
    DatePicker: {
      colorBgContainer: '#16213E',
      colorBgElevated: momentaColors.neutral[900],
    },

    // Tag
    Tag: {
      defaultBg: '#252A3D',
    },

    // Modal
    Modal: {
      headerBg: momentaColors.neutral[900],
      contentBg: momentaColors.neutral[900],
      footerBg: momentaColors.neutral[900],
    },

    // Drawer
    Drawer: {
      colorBgElevated: momentaColors.neutral[900],
    },

    // Tabs
    Tabs: {
      itemColor: 'rgba(255, 255, 255, 0.65)',
      itemSelectedColor: momentaColors.primary[400],
      itemHoverColor: momentaColors.primary[300],
      inkBarColor: momentaColors.primary[400],
    },

    // Progress
    Progress: {
      defaultColor: momentaColors.primary[400],
      remainingColor: '#2D3548',
    },

    // Alert
    Alert: {
      colorSuccessBg: 'rgba(0, 200, 83, 0.15)',
      colorSuccessBorder: '#00E676',
      colorWarningBg: 'rgba(255, 213, 79, 0.15)',
      colorWarningBorder: '#FFD54F',
      colorErrorBg: 'rgba(255, 82, 82, 0.15)',
      colorErrorBorder: '#FF5252',
      colorInfoBg: 'rgba(51, 133, 255, 0.15)',
      colorInfoBorder: momentaColors.primary[400],
    },

    // Tooltip
    Tooltip: {
      colorBgSpotlight: '#16213E',
      colorTextLightSolid: 'rgba(255, 255, 255, 0.87)',
    },

    // Popover
    Popover: {
      colorBgElevated: '#16213E',
    },

    // Notification
    Notification: {
      colorBgElevated: '#16213E',
    },

    // Breadcrumb
    Breadcrumb: {
      itemColor: 'rgba(255, 255, 255, 0.45)',
      lastItemColor: 'rgba(255, 255, 255, 0.87)',
      linkColor: 'rgba(255, 255, 255, 0.45)',
      linkHoverColor: momentaColors.primary[400],
      separatorColor: 'rgba(255, 255, 255, 0.25)',
    },

    // Pagination
    Pagination: {
      itemActiveBg: momentaColors.primary[500],
    },

    // Divider
    Divider: {
      colorSplit: '#2D3548',
    },

    // Typography
    Typography: {
      colorText: 'rgba(255, 255, 255, 0.87)',
      colorTextSecondary: 'rgba(255, 255, 255, 0.65)',
      colorLink: momentaColors.primary[400],
      colorLinkHover: momentaColors.primary[300],
      colorLinkActive: momentaColors.primary[500],
    },
  },
};

// =============================================================================
// THEME UTILITIES
// =============================================================================

/**
 * Get the appropriate theme based on dark mode preference
 */
export const getMomentaTheme = (isDarkMode: boolean): ThemeConfig => {
  return isDarkMode ? momentaDarkTheme : momentaLightTheme;
};

/**
 * Chart colors for data visualization
 */
export const momentaChartColors = {
  primary: [
    momentaColors.primary[500],
    momentaColors.primary[400],
    momentaColors.primary[300],
    momentaColors.primary[200],
    momentaColors.primary[100],
  ],
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
  status: {
    success: momentaColors.success.main,
    warning: momentaColors.warning.main,
    error: momentaColors.error.main,
    info: momentaColors.info.main,
  },
  sequential: [
    '#E6F0FF',
    '#CCE0FF',
    '#99C2FF',
    '#66A3FF',
    '#3385FF',
    '#0066FF',
    '#0052CC',
    '#003D99',
  ],
};

/**
 * CSS variables for use outside of Ant Design
 */
export const momentaCssVariables = `
:root {
  --momenta-primary: ${momentaColors.primary[500]};
  --momenta-primary-hover: ${momentaColors.primary[400]};
  --momenta-primary-active: ${momentaColors.primary[600]};
  --momenta-primary-bg: ${momentaColors.primary[50]};

  --momenta-success: ${momentaColors.success.main};
  --momenta-warning: ${momentaColors.warning.main};
  --momenta-error: ${momentaColors.error.main};
  --momenta-info: ${momentaColors.info.main};

  --momenta-text-primary: ${momentaColors.neutral[900]};
  --momenta-text-secondary: ${momentaColors.neutral[700]};
  --momenta-text-tertiary: ${momentaColors.neutral[600]};

  --momenta-bg-primary: #FFFFFF;
  --momenta-bg-secondary: ${momentaColors.neutral[50]};
  --momenta-bg-tertiary: ${momentaColors.neutral[100]};

  --momenta-border: ${momentaColors.neutral[200]};
  --momenta-border-secondary: ${momentaColors.neutral[100]};
}

[data-theme="dark"] {
  --momenta-primary: ${momentaColors.primary[400]};
  --momenta-primary-hover: ${momentaColors.primary[300]};
  --momenta-primary-active: ${momentaColors.primary[500]};
  --momenta-primary-bg: rgba(51, 133, 255, 0.15);

  --momenta-success: #00E676;
  --momenta-warning: #FFD54F;
  --momenta-error: #FF5252;
  --momenta-info: ${momentaColors.primary[400]};

  --momenta-text-primary: rgba(255, 255, 255, 0.87);
  --momenta-text-secondary: rgba(255, 255, 255, 0.65);
  --momenta-text-tertiary: rgba(255, 255, 255, 0.45);

  --momenta-bg-primary: ${momentaColors.neutral[900]};
  --momenta-bg-secondary: #16213E;
  --momenta-bg-tertiary: ${momentaColors.neutral[950]};

  --momenta-border: #2D3548;
  --momenta-border-secondary: #252A3D;
}
`;

export default momentaLightTheme;
