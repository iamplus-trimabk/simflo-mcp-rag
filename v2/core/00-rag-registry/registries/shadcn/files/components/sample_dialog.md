# Dialog Component

A modal dialog component with overlay and focus management.

## Installation

```bash
npm install @radix-ui/react-dialog
```

## Usage

```tsx
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "./dialog"

export function Example() {
  return (
    <Dialog>
      <DialogTrigger>Open Dialog</DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Are you sure?</DialogTitle>
          <DialogDescription>
            This action cannot be undone.
          </DialogDescription>
        </DialogHeader>
      </DialogContent>
    </Dialog>
  )
}
```

## Components

- `Dialog`: Main container component
- `DialogTrigger`: Element that opens the dialog
- `DialogContent`: Dialog content with overlay
- `DialogHeader`: Header section for dialog
- `DialogTitle`: Dialog title
- `DialogDescription`: Dialog description text

## Props

### Dialog
- `open`: boolean (controlled state)
- `defaultOpen`: boolean (uncontrolled state)
- `onOpenChange`: (open: boolean) => void

### DialogContent
- `className`: string
- `children`: ReactNode

### DialogTrigger
- `asChild`: boolean
- `className`: string
- `children`: ReactNode

## Features

- Focus management
- Escape key to close
- Click outside to close
- Accessibility attributes
- Smooth animations

## Examples

```tsx
// Basic dialog
<Dialog>
  <DialogTrigger asChild>
    <Button>Open</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogTitle>Confirmation</DialogTitle>
    <DialogDescription>
      Please confirm your action.
    </DialogDescription>
  </DialogContent>
</Dialog>

// Controlled dialog
const [isOpen, setIsOpen] = useState(false)

<Dialog open={isOpen} onOpenChange={setIsOpen}>
  {/* content */}
</Dialog>
```

## Accessibility

- Focus trapping
- ARIA attributes
- Screen reader support
- Keyboard navigation