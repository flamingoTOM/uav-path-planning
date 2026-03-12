---
name: momenta-web-skill
description: "IMPORTANT: Always consult this skill FIRST before writing any React UI code in this project — it contains the required Momenta brand theme, logo, favicon, and component patterns that all pages must follow. Use whenever the user asks to build, create, design, review, or fix any web page, dashboard, admin panel, sidebar, table, card, form, login page, or component using React and Ant Design (antd). Covers Momenta brand compliance: theme config with light/dark mode, ConfigProvider setup, vehicle fleet monitoring UI, and status indicators. Without this skill, the output will not match the Momenta design system (#0066FF, #1A1A2E, Inter font, 8px grid)."
---

# Momenta UI - Brand Design System with Ant Design

Expert guidance for building Momenta-branded React applications with Ant Design (antd). Implements Momenta's brand identity with intelligent, professional, and forward-thinking aesthetics suitable for autonomous driving technology interfaces.

## When to Apply

Reference these guidelines when:

- Building React applications for Momenta
- Designing admin panels, dashboards, or monitoring systems
- Implementing data-heavy interfaces with Momenta branding
- Creating vehicle data visualization or real-time monitoring UIs
- Reviewing code for Momenta brand compliance
- Customizing Ant Design themes for Momenta projects

---

## Momenta Brand Assets

### Logo

The Momenta logo is a bold, geometric "M" formed by two angled strokes in Momenta Blue (#0066FF) on a white background. The logo and favicon files are bundled in **this skill's `assets/` directory**.

| Asset             | Skill Source Path    | Size      | Usage                                                     |
| ----------------- | -------------------- | --------- | --------------------------------------------------------- |
| **Logo (PNG)**    | `assets/logo.png`    | 400x400px | Sidebar headers, login pages, about screens, splash pages |
| **Favicon (ICO)** | `assets/favicon.ico` | 32x32px   | Browser tab icon, bookmark icon                           |

> **IMPORTANT — Copy assets into the user's project:**
> When building a new project or adding Momenta branding, you MUST copy these files from the skill directory into the project:
>
> 1. **Logo** → copy `assets/logo.png` to the project's `src/assets/logo.png` (or the equivalent assets directory the project uses).
> 2. **Favicon** → copy `assets/favicon.ico` to the project's `public/favicon.ico`.
> 3. **Theme** → copy `assets/theme.ts` to the project's `src/theme.ts` (or equivalent) so the full Momenta theme config is available as a ready-to-import module.
>
> Without copying these files, `import logoSrc from "@/assets/logo.png"` and the favicon `<link>` will **break** at build time.

### Logo Usage Guidelines

| Guideline                | Specification                                                  |
| ------------------------ | -------------------------------------------------------------- |
| **Minimum clear space**  | 1/4 of logo height on all sides                                |
| **Minimum size**         | 24px height (collapsed sidebar), 32px+ (standard display)      |
| **On light backgrounds** | Use original Momenta Blue (#0066FF) logo                       |
| **On dark backgrounds**  | Use white (#FFFFFF) version or original on dark cards          |
| **Never**                | Stretch, rotate, recolor outside brand palette, or add effects |

### Applying Brand Assets in Code

#### Step 0 — Copy Skill Assets into the Project

Before using any brand asset, read the binary files from this skill's `assets/` directory and write them into the project. Use the project's actual paths (adjust if the project uses a different structure):

```bash
# Resolve the skill assets directory (this skill's assets/ folder)
# Copy logo into the project source assets
cp <skill_dir>/assets/logo.png   <project>/src/assets/logo.png

# Copy favicon into the project public directory
cp <skill_dir>/assets/favicon.ico <project>/public/favicon.ico

# Copy the full Momenta theme config (optional but recommended)
cp <skill_dir>/assets/theme.ts   <project>/src/theme.ts
```

#### Favicon Setup

```html
<!-- In index.html or document head (favicon.ico must already exist in /public) -->
<link rel="icon" type="image/x-icon" href="/favicon.ico" />
<link rel="icon" type="image/png" sizes="32x32" href="/favicon.ico" />
```

```tsx
// In Vite: place favicon.ico in /public directory
// vite.config.ts - no extra config needed, Vite serves /public files at root

// In Next.js: place favicon.ico in /app directory (App Router) or /public (Pages Router)
```

#### Logo Component

```tsx
import { theme } from "antd";
import logoSrc from "@/assets/logo.png";

interface MomentaLogoProps {
  collapsed?: boolean;
  showText?: boolean;
  className?: string;
}

const MomentaLogo: React.FC<MomentaLogoProps> = ({
  collapsed = false,
  showText = true,
  className,
}) => {
  const { token } = theme.useToken();

  return (
    <div
      className={className}
      style={{
        display: "flex",
        alignItems: "center",
        gap: collapsed ? 0 : 10,
        padding: "16px",
        cursor: "pointer",
      }}
    >
      <img
        src={logoSrc}
        alt="Momenta"
        style={{
          height: collapsed ? 24 : 32,
          width: "auto",
          transition: "height 0.2s ease",
        }}
      />
      {!collapsed && showText && (
        <span
          style={{
            fontSize: 18,
            fontWeight: 700,
            color: token.colorText,
            letterSpacing: "-0.02em",
            fontFamily: "'Inter', sans-serif",
            whiteSpace: "nowrap",
          }}
        >
          MOMENTA
        </span>
      )}
    </div>
  );
};
```

#### Logo in Sidebar

```tsx
// Sidebar follows the global theme automatically via ConfigProvider.
// No need to hardcode theme="dark" or background color.
<Sider
  collapsible
  collapsed={collapsed}
  onCollapse={setCollapsed}
  style={{ background: token.colorBgContainer }}
>
  <MomentaLogo collapsed={collapsed} />
  <Menu mode="inline" items={menuItems} />
</Sider>
```

#### Logo in Login Page

```tsx
<Flex vertical align="center" gap={24} style={{ marginBottom: 48 }}>
  <img src={logoSrc} alt="Momenta" style={{ height: 64, width: "auto" }} />
  <Typography.Title level={2} style={{ margin: 0 }}>
    MOMENTA
  </Typography.Title>
  <Typography.Text type="secondary">
    Autonomous Driving Management Platform
  </Typography.Text>
</Flex>
```

---

## Momenta Brand Philosophy

### Core Design Values

| Value                | Chinese | Principle                                 | Application                                  |
| -------------------- | ------- | ----------------------------------------- | -------------------------------------------- |
| **Intelligent**      | 智能    | Technology-forward, AI-powered aesthetics | Clean data visualization, smart interactions |
| **Trustworthy**      | 可信赖  | Stable, reliable, professional appearance | Consistent patterns, robust feedback         |
| **Forward-thinking** | 前瞻性  | Innovation, cutting-edge technology feel  | Modern UI patterns, smooth animations        |
| **Professional**     | 专业    | Enterprise-grade, polished interfaces     | Refined typography, precise spacing          |

### Design Principles

1. **Clarity** - Information hierarchy with clear visual weight
2. **Precision** - Pixel-perfect alignment and consistent spacing
3. **Intelligence** - Smart defaults and predictive interactions
4. **Trust** - Reliable feedback and consistent behavior
5. **Innovation** - Modern aesthetics without sacrificing usability
6. **Safety** - Clear status indicators and error states (critical for autonomous systems)

---

## Momenta Color System

### Primary Brand Colors

| Color Name             | Hex       | RGB                | Usage                                    |
| ---------------------- | --------- | ------------------ | ---------------------------------------- |
| **Momenta Blue**       | `#0066FF` | rgb(0, 102, 255)   | Primary brand color, CTAs, active states |
| **Momenta Blue Light** | `#3385FF` | rgb(51, 133, 255)  | Hover states, secondary accents          |
| **Momenta Blue Dark**  | `#0052CC` | rgb(0, 82, 204)    | Active/pressed states                    |
| **Tech Black**         | `#1A1A2E` | rgb(26, 26, 46)    | Primary text, headers, dark mode base    |
| **Deep Navy**          | `#16213E` | rgb(22, 33, 62)    | Secondary backgrounds, cards             |
| **Pure White**         | `#FFFFFF` | rgb(255, 255, 255) | Primary background, text on dark         |

### Extended Color Palette

#### Neutral Grays

| Level   | Hex       | Usage                               |
| ------- | --------- | ----------------------------------- |
| Gray 1  | `#FAFBFC` | Page background (light mode)        |
| Gray 2  | `#F4F5F7` | Card backgrounds, input backgrounds |
| Gray 3  | `#EBECF0` | Borders, dividers                   |
| Gray 4  | `#DFE1E6` | Disabled backgrounds                |
| Gray 5  | `#C1C7D0` | Placeholder text                    |
| Gray 6  | `#97A0AF` | Secondary text (light mode)         |
| Gray 7  | `#6B778C` | Tertiary text                       |
| Gray 8  | `#505F79` | Body text                           |
| Gray 9  | `#344563` | Emphasized text                     |
| Gray 10 | `#1A1A2E` | Primary text (Tech Black)           |

#### Functional Colors

| Purpose     | Primary   | Light BG  | Dark Accent | Usage                                   |
| ----------- | --------- | --------- | ----------- | --------------------------------------- |
| **Success** | `#00C853` | `#E8F9EE` | `#00A846`   | Confirmations, vehicle online status    |
| **Warning** | `#FFB800` | `#FFF8E6` | `#E6A600`   | Cautions, vehicle warnings              |
| **Error**   | `#FF3B3B` | `#FFEBEB` | `#E62E2E`   | Errors, critical alerts, vehicle faults |
| **Info**    | `#0066FF` | `#E6F0FF` | `#0052CC`   | Information, tips, notifications        |

#### Data Visualization Palette

| Index | Hex       | Name           | Use Case                       |
| ----- | --------- | -------------- | ------------------------------ |
| 1     | `#0066FF` | Momenta Blue   | Primary data series            |
| 2     | `#00C853` | Success Green  | Positive trends, online status |
| 3     | `#FFB800` | Warning Yellow | Attention items                |
| 4     | `#FF3B3B` | Alert Red      | Critical data, errors          |
| 5     | `#7C4DFF` | Tech Purple    | Secondary data series          |
| 6     | `#00BCD4` | Cyan           | Tertiary data, sensors         |
| 7     | `#FF6F00` | Orange         | Highlight data                 |
| 8     | `#E91E63` | Pink           | Accent data                    |

---

## Momenta Typography System

### Font Stack

```tsx
// Primary font family - Clean, modern, professional
fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif";

// Code/Monospace font family - For technical data
fontFamilyCode: "'JetBrains Mono', 'SF Mono', 'Fira Code', Consolas, monospace";

// Chinese font fallback
fontFamilyChinese: "'PingFang SC', 'Microsoft YaHei', 'Noto Sans SC', sans-serif";
```

### Type Scale

| Level      | Size | Line Height | Weight | Use Case                 |
| ---------- | ---- | ----------- | ------ | ------------------------ |
| H1         | 36px | 44px        | 600    | Page titles              |
| H2         | 28px | 36px        | 600    | Section headers          |
| H3         | 22px | 30px        | 600    | Card titles, modals      |
| H4         | 18px | 26px        | 600    | Subsection titles        |
| H5         | 16px | 24px        | 600    | Component headers        |
| Body       | 14px | 22px        | 400    | Primary body text        |
| Body Small | 12px | 20px        | 400    | Secondary text, captions |
| Code       | 13px | 20px        | 400    | Technical values, IDs    |

### Font Weight Guidelines

| Weight   | Value | Usage                           |
| -------- | ----- | ------------------------------- |
| Regular  | 400   | Body text, descriptions         |
| Medium   | 500   | Emphasized text, labels         |
| Semibold | 600   | Headings, buttons               |
| Bold     | 700   | Strong emphasis (use sparingly) |

---

## Ant Design Theme Configuration

### Complete Momenta Theme

```tsx
import { ConfigProvider, theme } from "antd";
import type { ThemeConfig } from "antd";

// Momenta Light Theme
export const momentaLightTheme: ThemeConfig = {
  token: {
    // Brand Colors
    colorPrimary: "#0066FF",
    colorSuccess: "#00C853",
    colorWarning: "#FFB800",
    colorError: "#FF3B3B",
    colorInfo: "#0066FF",

    // Text Colors
    colorText: "#1A1A2E",
    colorTextSecondary: "#505F79",
    colorTextTertiary: "#6B778C",
    colorTextQuaternary: "#97A0AF",

    // Background Colors
    colorBgContainer: "#FFFFFF",
    colorBgElevated: "#FFFFFF",
    colorBgLayout: "#FAFBFC",
    colorBgSpotlight: "rgba(26, 26, 46, 0.85)",
    colorBgMask: "rgba(26, 26, 46, 0.45)",

    // Border Colors
    colorBorder: "#EBECF0",
    colorBorderSecondary: "#F4F5F7",

    // Link Colors
    colorLink: "#0066FF",
    colorLinkHover: "#3385FF",
    colorLinkActive: "#0052CC",

    // Typography
    fontFamily:
      "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif",
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
    boxShadow:
      "0 1px 3px 0 rgba(26, 26, 46, 0.1), 0 1px 2px -1px rgba(26, 26, 46, 0.06)",
    boxShadowSecondary:
      "0 4px 6px -1px rgba(26, 26, 46, 0.1), 0 2px 4px -2px rgba(26, 26, 46, 0.06)",

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
    motionDurationFast: "0.1s",
    motionDurationMid: "0.2s",
    motionDurationSlow: "0.3s",
  },
  components: {
    Button: {
      colorPrimary: "#0066FF",
      algorithm: true,
      primaryShadow: "0 2px 4px rgba(0, 102, 255, 0.2)",
      fontWeight: 600,
    },
    Card: {
      headerBg: "#FAFBFC",
      colorBorderSecondary: "#EBECF0",
    },
    Table: {
      headerBg: "#FAFBFC",
      headerColor: "#1A1A2E",
      rowHoverBg: "#F4F5F7",
      borderColor: "#EBECF0",
    },
    Menu: {
      itemBg: "transparent",
      itemSelectedBg: "#E6F0FF",
      itemSelectedColor: "#0066FF",
      itemHoverBg: "#F4F5F7",
    },
    Input: {
      colorBorder: "#EBECF0",
      hoverBorderColor: "#0066FF",
      activeBorderColor: "#0066FF",
    },
    Select: {
      colorBorder: "#EBECF0",
      optionSelectedBg: "#E6F0FF",
    },
    Tag: {
      colorFillSecondary: "#E6F0FF",
    },
    Badge: {
      colorBgContainer: "#FF3B3B",
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
    colorPrimary: "#3385FF",
    colorSuccess: "#00E676",
    colorWarning: "#FFD54F",
    colorError: "#FF5252",
    colorInfo: "#3385FF",

    // Text Colors
    colorText: "rgba(255, 255, 255, 0.87)",
    colorTextSecondary: "rgba(255, 255, 255, 0.65)",
    colorTextTertiary: "rgba(255, 255, 255, 0.45)",
    colorTextQuaternary: "rgba(255, 255, 255, 0.25)",

    // Background Colors
    colorBgContainer: "#1A1A2E",
    colorBgElevated: "#16213E",
    colorBgLayout: "#0F0F1A",
    colorBgSpotlight: "rgba(255, 255, 255, 0.85)",
    colorBgMask: "rgba(0, 0, 0, 0.65)",

    // Border Colors
    colorBorder: "#2D3548",
    colorBorderSecondary: "#252A3D",

    // Typography
    fontFamily:
      "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif",
    fontFamilyCode: "'JetBrains Mono', 'SF Mono', Consolas, monospace",
    fontSize: 14,

    // Border Radius
    borderRadius: 6,
    borderRadiusLG: 8,
    borderRadiusSM: 4,

    // Shadows
    boxShadow:
      "0 1px 3px 0 rgba(0, 0, 0, 0.3), 0 1px 2px -1px rgba(0, 0, 0, 0.2)",
    boxShadowSecondary:
      "0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -2px rgba(0, 0, 0, 0.3)",
  },
  components: {
    Button: {
      colorPrimary: "#3385FF",
      algorithm: true,
      primaryShadow: "0 2px 8px rgba(51, 133, 255, 0.35)",
    },
    Card: {
      headerBg: "#16213E",
      colorBorderSecondary: "#2D3548",
    },
    Table: {
      headerBg: "#16213E",
      headerColor: "rgba(255, 255, 255, 0.87)",
      rowHoverBg: "#252A3D",
      borderColor: "#2D3548",
    },
    Menu: {
      itemBg: "#1A1A2E",
      subMenuItemBg: "#0F0F1A",
      itemSelectedBg: "rgba(51, 133, 255, 0.2)",
      itemSelectedColor: "#3385FF",
      itemHoverBg: "#252A3D",
    },
    Input: {
      colorBgContainer: "#16213E",
      colorBorder: "#2D3548",
    },
    Select: {
      colorBgContainer: "#16213E",
      colorBgElevated: "#1A1A2E",
      optionSelectedBg: "rgba(51, 133, 255, 0.2)",
    },
  },
};
```

### App Root Setup

```tsx
import React, { useState } from "react";
import { ConfigProvider, App } from "antd";
import zhCN from "antd/locale/zh_CN";
import enUS from "antd/locale/en_US";
import { momentaLightTheme, momentaDarkTheme } from "./theme";

interface MomentaAppProviderProps {
  children: React.ReactNode;
  locale?: "zh" | "en";
  darkMode?: boolean;
}

export const MomentaAppProvider: React.FC<MomentaAppProviderProps> = ({
  children,
  locale = "zh",
  darkMode = false,
}) => {
  return (
    <ConfigProvider
      locale={locale === "zh" ? zhCN : enUS}
      theme={darkMode ? momentaDarkTheme : momentaLightTheme}
    >
      <App>{children}</App>
    </ConfigProvider>
  );
};

// Usage with theme toggle
const MyApp: React.FC = () => {
  const [isDark, setIsDark] = useState(false);

  return (
    <MomentaAppProvider darkMode={isDark}>
      {/* Your application */}
    </MomentaAppProvider>
  );
};
```

---

## Component Patterns

### Dashboard Layout

```tsx
import React, { useState } from "react";
import { Layout, Menu, Flex, Typography, Avatar, Badge, theme } from "antd";
import {
  DashboardOutlined,
  CarOutlined,
  SettingOutlined,
  BellOutlined,
} from "@ant-design/icons";
import logoSrc from "@/assets/logo.png";

const { Header, Sider, Content } = Layout;
const { Title } = Typography;

const MomentaDashboard: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const { token } = theme.useToken();

  const menuItems = [
    { key: "dashboard", icon: <DashboardOutlined />, label: "Dashboard" },
    { key: "vehicles", icon: <CarOutlined />, label: "Vehicle Fleet" },
    { key: "settings", icon: <SettingOutlined />, label: "Settings" },
  ];

  return (
    <Layout style={{ minHeight: "100vh" }}>
      {/* Sidebar - uses theme tokens, adapts to light/dark mode */}
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        style={{
          background: token.colorBgContainer,
          borderRight: `1px solid ${token.colorBorder}`,
        }}
      >
        <Flex
          align="center"
          gap={collapsed ? 0 : 10}
          style={{ height: 64, padding: "0 16px" }}
        >
          <img
            src={logoSrc}
            alt="Momenta"
            style={{
              height: collapsed ? 24 : 32,
              width: "auto",
              transition: "height 0.2s ease",
            }}
          />
          {!collapsed && (
            <span
              style={{
                fontSize: 16,
                fontWeight: 700,
                color: token.colorText,
                letterSpacing: "-0.02em",
                whiteSpace: "nowrap",
              }}
            >
              MOMENTA
            </span>
          )}
        </Flex>
        <Menu mode="inline" items={menuItems} />
      </Sider>

      <Layout>
        {/* Header */}
        <Header
          style={{
            padding: "0 24px",
            background: token.colorBgContainer,
            borderBottom: `1px solid ${token.colorBorder}`,
          }}
        >
          <Flex
            justify="space-between"
            align="center"
            style={{ height: "100%" }}
          >
            <Title level={4} style={{ margin: 0 }}>
              Dashboard
            </Title>
            <Flex gap={16} align="center">
              <Badge count={5}>
                <BellOutlined style={{ fontSize: 20, cursor: "pointer" }} />
              </Badge>
              <Avatar style={{ backgroundColor: token.colorPrimary }}>M</Avatar>
            </Flex>
          </Flex>
        </Header>

        {/* Content */}
        <Content
          style={{
            margin: 24,
            padding: 24,
            background: token.colorBgContainer,
            borderRadius: token.borderRadiusLG,
            minHeight: 280,
          }}
        >
          {/* Page content */}
        </Content>
      </Layout>
    </Layout>
  );
};
```

### Vehicle Status Card

```tsx
import { Card, Flex, Typography, Tag, Space, Progress } from "antd";
import { CarOutlined, EnvironmentOutlined } from "@ant-design/icons";

interface VehicleCardProps {
  vehicleId: string;
  status: "online" | "offline" | "warning";
  location: string;
  battery: number;
  mileage: number;
}

const VehicleStatusCard: React.FC<VehicleCardProps> = ({
  vehicleId,
  status,
  location,
  battery,
  mileage,
}) => {
  const statusConfig = {
    online: { color: "#00C853", text: "Online" },
    offline: { color: "#97A0AF", text: "Offline" },
    warning: { color: "#FFB800", text: "Warning" },
  };

  return (
    <Card
      hoverable
      style={{ borderRadius: 8 }}
      styles={{ body: { padding: 20 } }}
    >
      <Flex justify="space-between" align="flex-start">
        <Space direction="vertical" size={4}>
          <Flex align="center" gap={8}>
            <CarOutlined style={{ fontSize: 24, color: "#0066FF" }} />
            <Typography.Title level={5} style={{ margin: 0 }}>
              {vehicleId}
            </Typography.Title>
          </Flex>
          <Flex align="center" gap={4}>
            <EnvironmentOutlined style={{ color: "#6B778C" }} />
            <Typography.Text type="secondary">{location}</Typography.Text>
          </Flex>
        </Space>
        <Tag color={statusConfig[status].color}>
          {statusConfig[status].text}
        </Tag>
      </Flex>

      <Flex gap={24} style={{ marginTop: 16 }}>
        <Space direction="vertical" size={4} style={{ flex: 1 }}>
          <Typography.Text type="secondary">Battery</Typography.Text>
          <Progress
            percent={battery}
            size="small"
            strokeColor={battery > 20 ? "#00C853" : "#FF3B3B"}
          />
        </Space>
        <Space direction="vertical" size={4} align="end">
          <Typography.Text type="secondary">Mileage</Typography.Text>
          <Typography.Text strong>
            {mileage.toLocaleString()} km
          </Typography.Text>
        </Space>
      </Flex>
    </Card>
  );
};
```

### Data Monitoring Table

```tsx
import { Table, Tag, Space, Button, Input } from "antd";
import type { TableColumnsType } from "antd";
import { SearchOutlined, FilterOutlined } from "@ant-design/icons";

interface VehicleData {
  key: string;
  id: string;
  status: "active" | "idle" | "maintenance" | "error";
  driver: string;
  speed: number;
  location: string;
  lastUpdate: string;
}

const statusConfig = {
  active: { color: "#00C853", text: "Active" },
  idle: { color: "#FFB800", text: "Idle" },
  maintenance: { color: "#0066FF", text: "Maintenance" },
  error: { color: "#FF3B3B", text: "Error" },
};

const columns: TableColumnsType<VehicleData> = [
  {
    title: "Vehicle ID",
    dataIndex: "id",
    key: "id",
    sorter: (a, b) => a.id.localeCompare(b.id),
    render: (id) => (
      <Typography.Text code style={{ color: "#0066FF" }}>
        {id}
      </Typography.Text>
    ),
  },
  {
    title: "Status",
    dataIndex: "status",
    key: "status",
    filters: Object.entries(statusConfig).map(([key, val]) => ({
      text: val.text,
      value: key,
    })),
    onFilter: (value, record) => record.status === value,
    render: (status: keyof typeof statusConfig) => (
      <Tag color={statusConfig[status].color}>{statusConfig[status].text}</Tag>
    ),
  },
  {
    title: "Driver",
    dataIndex: "driver",
    key: "driver",
  },
  {
    title: "Speed",
    dataIndex: "speed",
    key: "speed",
    sorter: (a, b) => a.speed - b.speed,
    render: (speed) => `${speed} km/h`,
  },
  {
    title: "Location",
    dataIndex: "location",
    key: "location",
  },
  {
    title: "Last Update",
    dataIndex: "lastUpdate",
    key: "lastUpdate",
  },
  {
    title: "Actions",
    key: "actions",
    fixed: "right",
    width: 150,
    render: () => (
      <Space size="small">
        <Button type="link" size="small">
          View
        </Button>
        <Button type="link" size="small">
          Logs
        </Button>
      </Space>
    ),
  },
];

const VehicleMonitoringTable: React.FC = () => (
  <Table
    columns={columns}
    dataSource={data}
    pagination={{
      showSizeChanger: true,
      showQuickJumper: true,
      showTotal: (total) => `Total ${total} vehicles`,
    }}
    scroll={{ x: 1200 }}
    sticky
  />
);
```

### Statistics Dashboard Cards

```tsx
import { Card, Statistic, Row, Col, Flex } from "antd";
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  CarOutlined,
  AlertOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
} from "@ant-design/icons";

const StatisticsCards: React.FC = () => (
  <Row gutter={[16, 16]}>
    <Col xs={24} sm={12} lg={6}>
      <Card>
        <Statistic
          title="Total Vehicles"
          value={1284}
          prefix={<CarOutlined style={{ color: "#0066FF" }} />}
          valueStyle={{ color: "#1A1A2E" }}
        />
      </Card>
    </Col>
    <Col xs={24} sm={12} lg={6}>
      <Card>
        <Statistic
          title="Active Now"
          value={892}
          prefix={<CheckCircleOutlined style={{ color: "#00C853" }} />}
          suffix={
            <span style={{ fontSize: 14, color: "#00C853" }}>
              <ArrowUpOutlined /> 12%
            </span>
          }
        />
      </Card>
    </Col>
    <Col xs={24} sm={12} lg={6}>
      <Card>
        <Statistic
          title="Alerts"
          value={23}
          prefix={<AlertOutlined style={{ color: "#FFB800" }} />}
          valueStyle={{ color: "#FFB800" }}
        />
      </Card>
    </Col>
    <Col xs={24} sm={12} lg={6}>
      <Card>
        <Statistic
          title="Avg. Trip Time"
          value={42}
          prefix={<ClockCircleOutlined style={{ color: "#6B778C" }} />}
          suffix="min"
        />
      </Card>
    </Col>
  </Row>
);
```

---

## Chart Configuration

### Chart Color Palette

Use these colors consistently across all data visualizations:

```tsx
export const momentaChartColors = {
  primary: ["#0066FF", "#3385FF", "#66A3FF", "#99C2FF", "#CCE0FF"],
  status: {
    success: "#00C853",
    warning: "#FFB800",
    error: "#FF3B3B",
    info: "#0066FF",
  },
  categorical: [
    "#0066FF", // Momenta Blue
    "#00C853", // Success Green
    "#7C4DFF", // Tech Purple
    "#00BCD4", // Cyan
    "#FF6F00", // Orange
    "#E91E63", // Pink
    "#FFB800", // Warning Yellow
    "#607D8B", // Blue Gray
  ],
  heatmap: {
    low: "#E6F0FF",
    medium: "#66A3FF",
    high: "#0066FF",
    critical: "#0052CC",
  },
};

// Chart theme for common libraries (ECharts, Chart.js, etc.)
export const momentaChartTheme = {
  backgroundColor: "transparent",
  textStyle: {
    fontFamily: "'Inter', sans-serif",
    color: "#505F79",
  },
  title: {
    textStyle: {
      color: "#1A1A2E",
      fontWeight: 600,
    },
  },
  legend: {
    textStyle: {
      color: "#505F79",
    },
  },
  tooltip: {
    backgroundColor: "#1A1A2E",
    borderColor: "#1A1A2E",
    textStyle: {
      color: "#FFFFFF",
    },
  },
  axis: {
    axisLine: { lineStyle: { color: "#EBECF0" } },
    axisTick: { lineStyle: { color: "#EBECF0" } },
    axisLabel: { color: "#6B778C" },
    splitLine: { lineStyle: { color: "#F4F5F7" } },
  },
};
```

---

## Best Practices

### DO's

| Category         | Best Practice                                                                |
| ---------------- | ---------------------------------------------------------------------------- |
| **Brand Colors** | Always use Momenta Blue (#0066FF) for primary actions and CTAs               |
| **Typography**   | Use Inter font family for all UI text                                        |
| **Dark Mode**    | Support dark mode with Tech Black (#1A1A2E) as base                          |
| **Status**       | Use consistent status colors: Green (success), Yellow (warning), Red (error) |
| **Spacing**      | Use 8px grid system (8, 16, 24, 32, 48)                                      |
| **Cards**        | Use subtle shadows and 8px border radius                                     |
| **Tables**       | Always include status indicators for vehicle/system data                     |
| **Icons**        | Use Ant Design icons with Momenta Blue for primary icons                     |
| **Feedback**     | Provide immediate visual feedback for all interactions                       |

### DON'Ts

| Category       | Anti-Pattern                                         |
| -------------- | ---------------------------------------------------- |
| **Colors**     | Don't use colors outside the Momenta palette         |
| **Typography** | Don't mix font families without purpose              |
| **Contrast**   | Don't use low-contrast text (minimum 4.5:1 ratio)    |
| **Spacing**    | Don't use arbitrary spacing values                   |
| **Icons**      | Don't use emojis for UI icons                        |
| **Status**     | Don't use non-standard colors for status indicators  |
| **Animation**  | Don't use excessive or slow animations               |
| **Layout**     | Don't overcrowd interfaces - maintain breathing room |

---

## Accessibility Guidelines

### Color Contrast

All text must meet WCAG 2.1 AA standards:

- Normal text: 4.5:1 minimum contrast ratio
- Large text (18px+ or 14px bold): 3:1 minimum
- Interactive elements: clear focus states

### Focus States

```tsx
// Add visible focus rings
<Button
  style={{
    outline: 'none',
  }}
  className="momenta-focusable"
/>

// CSS
.momenta-focusable:focus-visible {
  box-shadow: 0 0 0 2px #FFFFFF, 0 0 0 4px #0066FF;
}
```

### Motion

```tsx
// Respect reduced motion preferences
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

<ConfigProvider
  theme={{
    token: {
      motion: !prefersReducedMotion,
    },
  }}
>
```

---

## Pre-Delivery Checklist

Before delivering Momenta UI code, verify:

### Brand Compliance

- [ ] Primary color is Momenta Blue (#0066FF)
- [ ] Using Inter font family
- [ ] Status colors follow Momenta palette
- [ ] Dark mode supported with Tech Black base
- [ ] favicon.ico placed in public directory and linked in HTML head
- [ ] logo.png used in sidebar/header with proper sizing (24-32px height)
- [ ] Logo has adequate clear space and is not distorted

### Component Usage

- [ ] Using `App` component wrapper
- [ ] Forms use `Form.useForm()` hook
- [ ] Tables have unique `rowKey` prop
- [ ] Icons imported from `@ant-design/icons`

### Theming

- [ ] Using Design Tokens via ConfigProvider
- [ ] No CSS `!important` overrides
- [ ] Theme configuration matches Momenta standards

### Accessibility

- [ ] Color contrast meets WCAG standards
- [ ] Focus states are visible
- [ ] Motion respects user preferences
- [ ] All interactive elements are keyboard accessible

### Responsive

- [ ] Grid system used for layouts
- [ ] Tables have responsive scroll
- [ ] Components scale appropriately

### Performance

- [ ] Large lists use virtual scrolling
- [ ] Heavy components lazy loaded
- [ ] Bundle size optimized
