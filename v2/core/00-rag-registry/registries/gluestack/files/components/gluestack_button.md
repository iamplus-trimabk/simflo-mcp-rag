# Gluestack Button

A performant, accessible button component built with Gluestack UI.

## Installation

```bash
npm install @gluestack-ui/button
```

## Usage

```tsx
import { Button, ButtonText } from "@gluestack-ui/button"

export function Example() {
  return (
    <Button action="primary">
      <ButtonText>Click me</ButtonText>
    </Button>
  )
}
```

## Features

- Multiple action variants (primary, secondary, positive, negative)
- Size variants (sm, md, lg)
- Disabled state
- Loading state
- Full keyboard accessibility
- Focus management

## Variants

### Action Types
- `primary`: Primary action button
- `secondary`: Secondary action button
- `positive`: Positive/confirm action
- `negative`: Destructive action

### Size Variants
- `sm`: Small button (32px height)
- `md`: Medium button (40px height)
- `lg`: Large button (48px height)

## Props

### Button
- `action`: "primary" | "secondary" | "positive" | "negative"
- `size`: "sm" | "md" | "lg"
- `isDisabled`: boolean
- `isLoading`: boolean
- `isFocusVisible`: boolean

### ButtonText
- `isTruncated`: boolean
- `bold`: boolean
- `italic`: boolean
- `underline`: boolean

## Examples

```tsx
// Different actions
<Button action="primary">
  <ButtonText>Primary</ButtonText>
</Button>

<Button action="secondary">
  <ButtonText>Secondary</ButtonText>
</Button>

// Different sizes
<Button size="sm">
  <ButtonText>Small</ButtonText>
</Button>

<Button size="lg">
  <ButtonText>Large</ButtonText>
</Button>

// With loading state
<Button isLoading>
  <ButtonText>Loading...</ButtonText>
</Button>

// Disabled state
<Button isDisabled>
  <ButtonText>Disabled</ButtonText>
</Button>
```

## Styling

The button uses styled components with theme support. Colors and spacing can be customized through the Gluestack theme configuration.

## Accessibility

- Full keyboard navigation support
- Screen reader compatibility
- Focus management
- ARIA attributes
- High contrast mode support