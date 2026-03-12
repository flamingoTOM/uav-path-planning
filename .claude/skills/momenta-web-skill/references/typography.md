# Momenta Typography System Reference

Complete typography specification for Momenta brand UI.

## Font Families

### Primary Font: Inter

Inter is the primary font family for Momenta UI. It provides excellent readability, professional appearance, and comprehensive character support.

```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
```

**Google Fonts Import:**
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
```

### Monospace Font: JetBrains Mono

For code, technical data, vehicle IDs, and numeric displays.

```css
font-family: 'JetBrains Mono', 'SF Mono', 'Fira Code', Consolas, 'Liberation Mono', monospace;
```

**Google Fonts Import:**
```html
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
```

### Chinese Font Stack

For Chinese language support.

```css
font-family: 'PingFang SC', 'Microsoft YaHei', 'Noto Sans SC', 'Hiragino Sans GB', sans-serif;
```

## Type Scale

### Headings

| Level | Size | Line Height | Weight | Letter Spacing | Use Case |
|-------|------|-------------|--------|----------------|----------|
| H1 | 36px (2.25rem) | 44px (1.22) | 600 | -0.02em | Page titles |
| H2 | 28px (1.75rem) | 36px (1.29) | 600 | -0.015em | Section headers |
| H3 | 22px (1.375rem) | 30px (1.36) | 600 | -0.01em | Card titles, modal headers |
| H4 | 18px (1.125rem) | 26px (1.44) | 600 | -0.005em | Subsection titles |
| H5 | 16px (1rem) | 24px (1.5) | 600 | 0 | Component headers |
| H6 | 14px (0.875rem) | 22px (1.57) | 600 | 0 | Small headers |

### Body Text

| Type | Size | Line Height | Weight | Use Case |
|------|------|-------------|--------|----------|
| Body Large | 16px | 24px (1.5) | 400 | Emphasized paragraphs |
| **Body** | **14px** | **22px (1.57)** | **400** | **Primary body text** |
| Body Small | 12px | 20px (1.67) | 400 | Secondary text, captions |
| Body XS | 11px | 18px (1.64) | 400 | Labels, timestamps |

### UI Text

| Type | Size | Weight | Use Case |
|------|------|--------|----------|
| Button Large | 16px | 600 | Large buttons |
| **Button** | **14px** | **600** | **Standard buttons** |
| Button Small | 12px | 600 | Compact buttons |
| Label | 14px | 500 | Form labels |
| Label Small | 12px | 500 | Small labels |
| Caption | 12px | 400 | Captions, hints |
| Overline | 11px | 600 | Category labels (uppercase) |

### Numeric & Code

| Type | Size | Font | Weight | Use Case |
|------|------|------|--------|----------|
| Display Number | 48px | Inter | 600 | Hero statistics |
| Statistic | 28px | Inter | 600 | Dashboard cards |
| Metric | 20px | Inter | 500 | Inline metrics |
| Code Block | 13px | JetBrains Mono | 400 | Code displays |
| Inline Code | 13px | JetBrains Mono | 400 | Inline code |
| Vehicle ID | 14px | JetBrains Mono | 500 | Vehicle identifiers |
| Timestamp | 12px | JetBrains Mono | 400 | Dates/times |

## Font Weights

| Weight Name | Value | Usage |
|-------------|-------|-------|
| Regular | 400 | Body text, descriptions, paragraphs |
| Medium | 500 | Labels, emphasized text, metrics |
| Semibold | 600 | Headings, buttons, strong emphasis |
| Bold | 700 | Critical emphasis (use sparingly) |

## Line Height Guidelines

| Content Type | Line Height | Ratio |
|--------------|-------------|-------|
| Headings | Tight | 1.2 - 1.4 |
| Body text | Normal | 1.5 - 1.6 |
| UI components | Comfortable | 1.4 - 1.5 |
| Dense tables | Compact | 1.3 - 1.4 |

## Text Colors

### Light Mode

| Type | Color | Hex | Usage |
|------|-------|-----|-------|
| Primary | Tech Black | `#1A1A2E` | Headings, important text |
| Secondary | Dark Gray | `#505F79` | Body text, descriptions |
| Tertiary | Medium Gray | `#6B778C` | Secondary info, labels |
| Quaternary | Light Gray | `#97A0AF` | Placeholders, disabled |
| Link | Momenta Blue | `#0066FF` | Interactive text |
| Link Hover | Blue Light | `#3385FF` | Link hover state |
| Success | Green | `#00C853` | Positive messaging |
| Warning | Yellow | `#FFB800` | Warning text |
| Error | Red | `#FF3B3B` | Error messaging |

### Dark Mode

| Type | Color | Value | Usage |
|------|-------|-------|-------|
| Primary | White 87% | `rgba(255,255,255,0.87)` | Headings, important text |
| Secondary | White 65% | `rgba(255,255,255,0.65)` | Body text |
| Tertiary | White 45% | `rgba(255,255,255,0.45)` | Secondary info |
| Quaternary | White 25% | `rgba(255,255,255,0.25)` | Placeholders |
| Link | Blue Light | `#3385FF` | Interactive text |

## Ant Design Typography Configuration

```tsx
import { ConfigProvider } from 'antd';

<ConfigProvider
  theme={{
    token: {
      // Font Families
      fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      fontFamilyCode: "'JetBrains Mono', 'SF Mono', Consolas, monospace",

      // Base Font Size
      fontSize: 14,

      // Font Sizes
      fontSizeSM: 12,
      fontSizeLG: 16,
      fontSizeXL: 20,
      fontSizeHeading1: 36,
      fontSizeHeading2: 28,
      fontSizeHeading3: 22,
      fontSizeHeading4: 18,
      fontSizeHeading5: 16,

      // Line Heights
      lineHeight: 1.5714285714,
      lineHeightSM: 1.6666666667,
      lineHeightLG: 1.5,
      lineHeightHeading1: 1.2222222222,
      lineHeightHeading2: 1.2857142857,
      lineHeightHeading3: 1.3636363636,
      lineHeightHeading4: 1.4444444444,
      lineHeightHeading5: 1.5,

      // Font Weight
      fontWeightStrong: 600,
    },
  }}
>
```

## Typography Components

### Ant Design Typography Usage

```tsx
import { Typography } from 'antd';

const { Title, Paragraph, Text, Link } = Typography;

// Page Title
<Title level={1}>Dashboard Overview</Title>

// Section Header
<Title level={2}>Vehicle Fleet Status</Title>

// Card Title
<Title level={3}>Active Vehicles</Title>

// Body Text
<Paragraph>
  Monitor real-time status of your autonomous vehicle fleet.
  Track location, battery levels, and operational metrics.
</Paragraph>

// Text Variations
<Text>Primary text</Text>
<Text type="secondary">Secondary text</Text>
<Text type="success">Success message</Text>
<Text type="warning">Warning message</Text>
<Text type="danger">Error message</Text>

// Code and Technical
<Text code>VEHICLE-001</Text>
<Text copyable>Copy this text</Text>

// Links
<Link href="/vehicles">View All Vehicles</Link>
```

### Custom Momenta Typography Components

```tsx
// Vehicle ID Display
const VehicleId: React.FC<{ id: string }> = ({ id }) => (
  <Text
    code
    style={{
      fontFamily: "'JetBrains Mono', monospace",
      fontWeight: 500,
      color: '#0066FF',
      backgroundColor: '#E6F0FF',
      padding: '2px 8px',
      borderRadius: 4,
    }}
  >
    {id}
  </Text>
);

// Metric Display
const MetricValue: React.FC<{ value: number; unit: string }> = ({ value, unit }) => (
  <Space size={4}>
    <Text
      style={{
        fontFamily: "'Inter', sans-serif",
        fontSize: 28,
        fontWeight: 600,
        color: '#1A1A2E',
      }}
    >
      {value.toLocaleString()}
    </Text>
    <Text
      style={{
        fontSize: 14,
        color: '#6B778C',
      }}
    >
      {unit}
    </Text>
  </Space>
);

// Status Label
const StatusLabel: React.FC<{ status: 'online' | 'offline' | 'warning' }> = ({ status }) => {
  const config = {
    online: { color: '#00C853', bg: '#E8F9EE' },
    offline: { color: '#6B778C', bg: '#F4F5F7' },
    warning: { color: '#FFB800', bg: '#FFF8E6' },
  };

  return (
    <Text
      style={{
        fontSize: 11,
        fontWeight: 600,
        textTransform: 'uppercase',
        letterSpacing: '0.05em',
        color: config[status].color,
        backgroundColor: config[status].bg,
        padding: '2px 8px',
        borderRadius: 4,
      }}
    >
      {status}
    </Text>
  );
};
```

## CSS Typography Classes

```css
/* Momenta Typography Classes */

/* Headings */
.momenta-h1 {
  font-family: 'Inter', sans-serif;
  font-size: 36px;
  font-weight: 600;
  line-height: 44px;
  letter-spacing: -0.02em;
  color: #1A1A2E;
}

.momenta-h2 {
  font-family: 'Inter', sans-serif;
  font-size: 28px;
  font-weight: 600;
  line-height: 36px;
  letter-spacing: -0.015em;
  color: #1A1A2E;
}

.momenta-h3 {
  font-family: 'Inter', sans-serif;
  font-size: 22px;
  font-weight: 600;
  line-height: 30px;
  letter-spacing: -0.01em;
  color: #1A1A2E;
}

/* Body Text */
.momenta-body {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 400;
  line-height: 22px;
  color: #505F79;
}

.momenta-body-sm {
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  font-weight: 400;
  line-height: 20px;
  color: #6B778C;
}

/* UI Text */
.momenta-label {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 500;
  line-height: 22px;
  color: #1A1A2E;
}

.momenta-caption {
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  font-weight: 400;
  line-height: 20px;
  color: #6B778C;
}

.momenta-overline {
  font-family: 'Inter', sans-serif;
  font-size: 11px;
  font-weight: 600;
  line-height: 18px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #97A0AF;
}

/* Code & Technical */
.momenta-code {
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  font-weight: 400;
  line-height: 20px;
  background-color: #F4F5F7;
  padding: 2px 6px;
  border-radius: 4px;
}

.momenta-vehicle-id {
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
  font-weight: 500;
  color: #0066FF;
}

.momenta-metric {
  font-family: 'Inter', sans-serif;
  font-size: 28px;
  font-weight: 600;
  color: #1A1A2E;
}

/* Dark Mode Overrides */
[data-theme="dark"] .momenta-h1,
[data-theme="dark"] .momenta-h2,
[data-theme="dark"] .momenta-h3 {
  color: rgba(255, 255, 255, 0.87);
}

[data-theme="dark"] .momenta-body {
  color: rgba(255, 255, 255, 0.65);
}

[data-theme="dark"] .momenta-body-sm,
[data-theme="dark"] .momenta-caption {
  color: rgba(255, 255, 255, 0.45);
}

[data-theme="dark"] .momenta-code {
  background-color: #252A3D;
  color: rgba(255, 255, 255, 0.87);
}
```

## Best Practices

### DO
- Use Inter for all UI text
- Use JetBrains Mono for code and technical data
- Maintain consistent hierarchy with heading levels
- Use appropriate line heights for readability
- Apply proper letter-spacing for headings

### DON'T
- Mix multiple font families unnecessarily
- Use font weights below 400 or above 700
- Skip heading levels (H1 -> H3)
- Use line heights below 1.2 for body text
- Apply letter-spacing to body text
