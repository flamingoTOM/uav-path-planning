# Momenta Color System Reference

Complete color specification for Momenta brand UI.

## Primary Brand Colors

### Momenta Blue Palette
| Name | Hex | RGB | HSL | Token |
|------|-----|-----|-----|-------|
| Blue 50 | `#E6F0FF` | rgb(230, 240, 255) | hsl(216, 100%, 95%) | `colorPrimaryBg` |
| Blue 100 | `#CCE0FF` | rgb(204, 224, 255) | hsl(216, 100%, 90%) | `colorPrimaryBgHover` |
| Blue 200 | `#99C2FF` | rgb(153, 194, 255) | hsl(216, 100%, 80%) | `colorPrimaryBorder` |
| Blue 300 | `#66A3FF` | rgb(102, 163, 255) | hsl(216, 100%, 70%) | `colorPrimaryBorderHover` |
| Blue 400 | `#3385FF` | rgb(51, 133, 255) | hsl(216, 100%, 60%) | `colorPrimaryHover` |
| **Blue 500** | **`#0066FF`** | rgb(0, 102, 255) | hsl(216, 100%, 50%) | **`colorPrimary`** |
| Blue 600 | `#0052CC` | rgb(0, 82, 204) | hsl(216, 100%, 40%) | `colorPrimaryActive` |
| Blue 700 | `#003D99` | rgb(0, 61, 153) | hsl(216, 100%, 30%) | `colorPrimaryTextHover` |
| Blue 800 | `#002966` | rgb(0, 41, 102) | hsl(216, 100%, 20%) | `colorPrimaryText` |
| Blue 900 | `#001433` | rgb(0, 20, 51) | hsl(216, 100%, 10%) | `colorPrimaryTextActive` |

### Tech Black Palette
| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| Black 50 | `#F4F5F7` | rgb(244, 245, 247) | Light background |
| Black 100 | `#EBECF0` | rgb(235, 236, 240) | Borders |
| Black 200 | `#DFE1E6` | rgb(223, 225, 230) | Disabled states |
| Black 300 | `#C1C7D0` | rgb(193, 199, 208) | Placeholder |
| Black 400 | `#97A0AF` | rgb(151, 160, 175) | Tertiary text |
| Black 500 | `#6B778C` | rgb(107, 119, 140) | Secondary text |
| Black 600 | `#505F79` | rgb(80, 95, 121) | Body text |
| Black 700 | `#344563` | rgb(52, 69, 99) | Emphasized text |
| Black 800 | `#252A3D` | rgb(37, 42, 61) | Dark elevated |
| Black 900 | `#1A1A2E` | rgb(26, 26, 46) | **Tech Black (Primary)** |
| Black 950 | `#0F0F1A` | rgb(15, 15, 26) | Dark mode layout |

## Functional Colors

### Success Green
| Name | Hex | Usage |
|------|-----|-------|
| Success 50 | `#E8F9EE` | Background |
| Success 100 | `#C3EFCF` | Light accent |
| Success 200 | `#85E0A3` | Border |
| Success 300 | `#47D17B` | Hover |
| Success 400 | `#1BC554` | |
| **Success 500** | **`#00C853`** | **Primary success** |
| Success 600 | `#00A846` | Active |
| Success 700 | `#008738` | Text |
| Success 800 | `#00662A` | Dark |
| Success 900 | `#00451C` | Darkest |

### Warning Yellow
| Name | Hex | Usage |
|------|-----|-------|
| Warning 50 | `#FFF8E6` | Background |
| Warning 100 | `#FFEFC2` | Light accent |
| Warning 200 | `#FFE08A` | Border |
| Warning 300 | `#FFD152` | Hover |
| Warning 400 | `#FFC41A` | |
| **Warning 500** | **`#FFB800`** | **Primary warning** |
| Warning 600 | `#E6A600` | Active |
| Warning 700 | `#CC9300` | Text |
| Warning 800 | `#997000` | Dark |
| Warning 900 | `#664A00` | Darkest |

### Error Red
| Name | Hex | Usage |
|------|-----|-------|
| Error 50 | `#FFEBEB` | Background |
| Error 100 | `#FFCCCC` | Light accent |
| Error 200 | `#FF9999` | Border |
| Error 300 | `#FF6666` | Hover |
| Error 400 | `#FF4747` | |
| **Error 500** | **`#FF3B3B`** | **Primary error** |
| Error 600 | `#E62E2E` | Active |
| Error 700 | `#CC2222` | Text |
| Error 800 | `#991919` | Dark |
| Error 900 | `#661111` | Darkest |

## Data Visualization Colors

### Primary Series
```typescript
export const chartColorsPrimary = [
  '#0066FF', // Momenta Blue
  '#00C853', // Success Green
  '#7C4DFF', // Tech Purple
  '#00BCD4', // Cyan
  '#FF6F00', // Orange
  '#E91E63', // Pink
  '#FFB800', // Warning Yellow
  '#607D8B', // Blue Gray
];
```

### Sequential (Blue)
```typescript
export const chartColorsSequential = [
  '#E6F0FF',
  '#CCE0FF',
  '#99C2FF',
  '#66A3FF',
  '#3385FF',
  '#0066FF',
  '#0052CC',
  '#003D99',
];
```

### Diverging (Blue-Red)
```typescript
export const chartColorsDiverging = [
  '#0066FF', // Strong negative
  '#3385FF',
  '#66A3FF',
  '#F4F5F7', // Neutral
  '#FF9999',
  '#FF6666',
  '#FF3B3B', // Strong positive
];
```

## Dark Mode Adjustments

| Light Mode | Dark Mode | Purpose |
|------------|-----------|---------|
| `#0066FF` | `#3385FF` | Primary color (brighter for dark bg) |
| `#00C853` | `#00E676` | Success (brighter) |
| `#FFB800` | `#FFD54F` | Warning (brighter) |
| `#FF3B3B` | `#FF5252` | Error (brighter) |
| `#FFFFFF` | `#1A1A2E` | Background swap |
| `#1A1A2E` | `rgba(255,255,255,0.87)` | Text swap |
| `#FAFBFC` | `#0F0F1A` | Layout background |
| `#EBECF0` | `#2D3548` | Border |

## CSS Variables Export

```css
:root {
  /* Primary */
  --momenta-primary: #0066FF;
  --momenta-primary-hover: #3385FF;
  --momenta-primary-active: #0052CC;
  --momenta-primary-bg: #E6F0FF;

  /* Text */
  --momenta-text-primary: #1A1A2E;
  --momenta-text-secondary: #505F79;
  --momenta-text-tertiary: #6B778C;
  --momenta-text-quaternary: #97A0AF;

  /* Background */
  --momenta-bg-primary: #FFFFFF;
  --momenta-bg-secondary: #FAFBFC;
  --momenta-bg-tertiary: #F4F5F7;

  /* Border */
  --momenta-border-primary: #EBECF0;
  --momenta-border-secondary: #DFE1E6;

  /* Functional */
  --momenta-success: #00C853;
  --momenta-warning: #FFB800;
  --momenta-error: #FF3B3B;
  --momenta-info: #0066FF;
}

[data-theme="dark"] {
  --momenta-primary: #3385FF;
  --momenta-primary-hover: #66A3FF;
  --momenta-primary-active: #0066FF;
  --momenta-primary-bg: rgba(0, 102, 255, 0.15);

  --momenta-text-primary: rgba(255, 255, 255, 0.87);
  --momenta-text-secondary: rgba(255, 255, 255, 0.65);
  --momenta-text-tertiary: rgba(255, 255, 255, 0.45);
  --momenta-text-quaternary: rgba(255, 255, 255, 0.25);

  --momenta-bg-primary: #1A1A2E;
  --momenta-bg-secondary: #16213E;
  --momenta-bg-tertiary: #0F0F1A;

  --momenta-border-primary: #2D3548;
  --momenta-border-secondary: #252A3D;

  --momenta-success: #00E676;
  --momenta-warning: #FFD54F;
  --momenta-error: #FF5252;
  --momenta-info: #3385FF;
}
```

## Tailwind CSS Config

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        momenta: {
          blue: {
            50: '#E6F0FF',
            100: '#CCE0FF',
            200: '#99C2FF',
            300: '#66A3FF',
            400: '#3385FF',
            500: '#0066FF',
            600: '#0052CC',
            700: '#003D99',
            800: '#002966',
            900: '#001433',
          },
          black: {
            50: '#F4F5F7',
            100: '#EBECF0',
            200: '#DFE1E6',
            300: '#C1C7D0',
            400: '#97A0AF',
            500: '#6B778C',
            600: '#505F79',
            700: '#344563',
            800: '#252A3D',
            900: '#1A1A2E',
            950: '#0F0F1A',
          },
          success: '#00C853',
          warning: '#FFB800',
          error: '#FF3B3B',
        },
      },
    },
  },
};
```
