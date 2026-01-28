# Protocol Design System

Design patterns and styling reference for the Protocol frontend.

## Core Principles

- **Light modern aesthetic** with clean whites and subtle grays
- **Black accents** for primary actions and key value displays
- **Minimal shadows** using `shadow-sm` for subtle depth
- **Strong typography** using `font-black` for values

---

## Background Patterns

### Dot Grid
```css
.dot-grid-bg {
  background-image: radial-gradient(#000 1px, transparent 1px);
  background-size: 40px 40px;
}
/* Apply with opacity-[0.03] for very subtle effect */
```

---

## Card Styling

### Default Card
```jsx
<div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
  {children}
</div>
```

### Highlight Card
```jsx
<div className="bg-gray-50 border border-gray-200 rounded-xl p-6">
  {children}
</div>
```

---

## Button Variants

### Primary (Black)
```jsx
className="bg-black text-white hover:bg-gray-800 shadow-md"
```

### Secondary
```jsx
className="bg-gray-100 text-gray-900 hover:bg-gray-200 border border-gray-200"
```

### Outline
```jsx
className="border border-gray-200 text-gray-600 hover:border-black hover:text-black"
```

### Ghost (for dark backgrounds)
```jsx
className="bg-white/10 text-white hover:bg-white/20 backdrop-blur-sm"
```

---

## Typography

### Labels
```jsx
className="text-xs font-bold text-gray-400 uppercase tracking-wider"
```

### Values (Large)
```jsx
className="text-4xl font-black text-gray-900 tracking-tight"
```

### Values (Medium)
```jsx
className="text-2xl font-black text-gray-900"
```

### Headings
```jsx
className="font-extrabold tracking-tight"
```

---

## Total Value Bar (Key Accent Element)

The black accent bar is used for hero/featured value displays:

```jsx
<div className="bg-black rounded-2xl p-8 text-white shadow-2xl">
  <div className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">
    Label
  </div>
  <div className="text-5xl font-black tracking-tighter">
    {value}
  </div>
</div>
```

### Pills on dark background
```jsx
{/* Info pill */}
<div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/10 backdrop-blur-sm">
  <span className="text-xs text-gray-400">Label:</span>
  <span className="text-sm text-white font-mono font-medium">{value}</span>
</div>

{/* Status pill */}
<div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/20 backdrop-blur-sm">
  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
  <span className="text-sm text-emerald-300 font-mono">{value}</span>
</div>
```

---

## Input Fields

```jsx
<input
  className="rounded-xl border-gray-200 bg-white border p-4 font-bold focus:border-black focus:ring-0"
/>
```

---

## Section Backgrounds

### Dashboard
```jsx
className="bg-gray-50/50"
```

### Footer
```jsx
className="border-t border-gray-100"
```

---

## Hero Section

```jsx
<section className="min-h-screen flex items-center justify-center">
  {/* Dot grid with very subtle opacity */}
  <div className="absolute inset-0 dot-grid-bg opacity-[0.03]" />

  {/* Bouncing icon */}
  <div className="w-20 h-20 rounded-2xl bg-gray-50 border border-gray-100 flex items-center justify-center animate-bounce">
    {icon}
  </div>

  {/* Form container */}
  <div className="bg-white p-2 rounded-2xl border border-gray-200 shadow-sm">
    {input}
  </div>
</section>
```

---

## Color Palette Summary

| Use Case | Class |
|----------|-------|
| Primary action | `bg-black` |
| Primary hover | `bg-gray-800` |
| Card background | `bg-white` |
| Card border | `border-gray-100` |
| Highlight bg | `bg-gray-50` |
| Highlight border | `border-gray-200` |
| Label text | `text-gray-400` |
| Body text | `text-gray-600` |
| Heading text | `text-gray-900` |
| Success | `bg-emerald-500` |
