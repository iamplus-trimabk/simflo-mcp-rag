# Button Component

A versatile button component for React applications with multiple variants and sizes.

## Installation

```bash
npm install @radix-ui/react-slot
```

## Usage

```tsx
import { Button } from "./button"

export function Example() {
  return (
    <Button variant="default">
      Click me
    </Button>
  )
}
```

## Props

- `variant`: "default" | "destructive" | "outline" | "secondary" | "ghost" | "link"
- `size`: "default" | "sm" | "lg" | "icon"
- `asChild`: boolean
- `className`: string

## Variants

### Default Button
Standard button styling with primary color.

### Outline Button
Button with outline styling, no background fill.

### Ghost Button
Transparent button with hover effects.

## Examples

```tsx
// Different variants
<Button variant="default">Default</Button>
<Button variant="outline">Outline</Button>
<Button variant="ghost">Ghost</Button>

// Different sizes
<Button size="sm">Small</Button>
<Button size="default">Default</Button>
<Button size="lg">Large</Button>
```

## Dependencies

- @radix-ui/react-slot
- class-variance-authority
- cn utility function

## Accessibility

- Supports keyboard navigation
- Screen reader friendly
- Focus management included