# SimFlo MCP RAG - React Native User Guide

This guide provides step-by-step instructions for setting up and using the SimFlo MCP RAG system with React Native applications.

## Quick Start

### 1. Start the Server

First, navigate to your SimFlo MCP RAG project directory and start the services:

```bash
# Navigate to project directory
cd /Users/tbardale/v2/simflo-mcp-rag

# Start the Python API server (runs in background)
cd data-pipeline
python3 api_server.py --host 127.0.0.1 --port 8000 &
cd ..

# Verify the server is running
curl -s http://127.0.0.1:8000/health
```

Expected output:
```json
{
  "status": "healthy",
  "timestamp": "2025-09-28T04:00:00.000Z",
  "database": "connected",
  "vector_store": "ready"
}
```

### 2. Add to Claude Desktop

**Manual MCP Configuration:**

1. Open Claude Desktop app
2. Go to Settings → Developer → Edit MCP Servers
3. Add the following configuration to your MCP settings:

```json
{
  "mcpServers": {
    "simflo-rag": {
      "command": "node",
      "args": ["/Users/tbardale/v2/simflo-mcp-rag/mcp-server/dist/index.js"],
      "env": {
        "API_BASE_URL": "http://127.0.0.1:8000",
        "LOG_LEVEL": "debug"
      }
    }
  }
}
```

4. Save the configuration and restart Claude Desktop

**Add to Cursor:**

1. Open Cursor
2. Go to Settings → Extensions → MCP
3. Add the same configuration as above
4. Restart Cursor

### 3. Verify MCP Connection

**List Available Tools:**

Ask Claude: "List all available MCP tools"

Expected response:
```
Available MCP Tools:
1. search_components - Search for components using natural language
2. get_component_details - Get detailed information about a specific component
3. get_component_installation - Get installation instructions and dependencies
4. list_components - List components by type or category
```

**Set Context:**

Tell Claude: "I'm working on a React Native project using Expo. I need help finding and implementing mobile UI components."

### 4. Test Component Documentation Retrieval

**Test Input Component:**

**Prompt:** "Using the MCP tools, search for React Native input components and show me exactly what the MCP system returns for text input components."

**Expected MCP Response Structure:**
```json
{
  "components": [
    {
      "name": "TextInput",
      "description": "React Native text input component with mobile-specific features",
      "platform": ["reactnative"],
      "files": [
        {
          "path": "components/ui/TextInput.tsx",
          "content": "import React from 'react';\nimport { TextInput as RNTextInput, View, Text, StyleSheet } from 'react-native';\nimport { cn } from '../lib/utils';\n\ninterface TextInputProps {\n  value?: string;\n  onChangeText?: (text: string) => void;\n  placeholder?: string;\n  secureTextEntry?: boolean;\n  keyboardType?: 'default' | 'email-address' | 'numeric' | 'phone-pad';\n  autoCapitalize?: 'none' | 'sentences' | 'words' | 'characters';\n  autoCorrect?: boolean;\n  error?: boolean;\n  label?: string;\n  className?: string;\n}\n\nexport const TextInput: React.FC<TextInputProps> = ({\n  value,\n  onChangeText,\n  placeholder,\n  secureTextEntry = false,\n  keyboardType = 'default',\n  autoCapitalize = 'none',\n  autoCorrect = true,\n  error = false,\n  label,\n  className\n}) => {\n  return (\n    <View style={styles.container}>\n      {label && <Text style={styles.label}>{label}</Text>}\n      <RNTextInput\n        value={value}\n        onChangeText={onChangeText}\n        placeholder={placeholder}\n        secureTextEntry={secureTextEntry}\n        keyboardType={keyboardType}\n        autoCapitalize={autoCapitalize}\n        autoCorrect={autoCorrect}\n        style={[\n          styles.input,\n          error && styles.inputError,\n          className\n        ]}\n        placeholderTextColor=\"#9CA3AF\"\n      />\n    </View>\n  );\n};\n\nconst styles = StyleSheet.create({\n  container: {\n    marginBottom: 16,\n  },\n  label: {\n    fontSize: 14,\n    fontWeight: '600',\n    color: '#374151',\n    marginBottom: 6,\n  },\n  input: {\n    height: 48,\n    borderWidth: 1,\n    borderColor: '#D1D5DB',\n    borderRadius: 8,\n    paddingHorizontal: 16,\n    fontSize: 16,\n    backgroundColor: '#FFFFFF',\n  },\n  inputError: {\n    borderColor: '#EF4444',\n  },\n});",
          "language": "tsx",
          "component_type": "component",
          "props_info": {
            "props": [
              {
                "name": "value",
                "type": "string",
                "description": "Input text value"
              },
              {
                "name": "onChangeText",
                "type": "function",
                "description": "Text change handler"
              },
              {
                "name": "placeholder",
                "type": "string",
                "description": "Placeholder text"
              },
              {
                "name": "secureTextEntry",
                "type": "boolean",
                "default": "false",
                "description": "Hide text input (for passwords)"
              },
              {
                "name": "keyboardType",
                "type": "string",
                "default": "'default'",
                "description": "Keyboard type (email, numeric, phone-pad)"
              },
              {
                "name": "label",
                "type": "string",
                "description": "Input field label"
              },
              {
                "name": "error",
                "type": "boolean",
                "default": "false",
                "description": "Error state styling"
              }
            ],
            "interface_name": "TextInputProps",
            "has_children": false,
            "is_functional": true
          }
        }
      ],
      "dependencies": ["react-native"],
      "installation": "npm install react-native",
      "usage_examples": [
        "<TextInput label=\"Email\" placeholder=\"Enter your email\" keyboardType=\"email-address\" />",
        "<TextInput label=\"Password\" placeholder=\"Enter password\" secureTextEntry={true} error={hasError} />"
      ]
    }
  ]
}
```

**Test Form Component:**

**Prompt:** "Search for React Native form components using MCP and show me the exact response structure for mobile form validation."

**Expected Response:**
```json
{
  "components": [
    {
      "name": "Form",
      "description": "React Native form component with touch-friendly validation and submission",
      "platform": ["reactnative"],
      "features": ["touch friendly", "validation", "keyboard handling"],
      "props_info": {
        "props": [
          {
            "name": "onSubmit",
            "type": "function",
            "required": true,
            "description": "Form submission handler"
          },
          {
            "name": "validationSchema",
            "type": "object",
            "description": "Yup validation schema"
          },
          {
            "name": "scrollEnabled",
            "type": "boolean",
            "default": "true",
            "description": "Enable scrolling for long forms"
          }
        ]
      },
      "dependencies": ["yup", "@hookform/resolvers", "react-hook-form"],
      "installation": "npm install yup @hookform/resolvers react-hook-form",
      "usage_examples": [
        "<Form onSubmit={handleSubmit} validationSchema={loginSchema}>",
        "  <TextInput name=\"email\" label=\"Email\" required />",
        "  <TextInput name=\"password\" label=\"Password\" secureTextEntry required />",
        "  <Button title=\"Login\" onPress={handleSubmit} />",
        "</Form>"
      ]
    }
  ]
}
```

**Test Table Component:**

**Prompt:** "Find React Native table components and show me the exact MCP response for data table components."

**Expected Response:**
```json
{
  "components": [
    {
      "name": "DataTable",
      "description": "Responsive data table component for React Native with horizontal scrolling",
      "platform": ["reactnative"],
      "features": ["horizontal scroll", "sticky headers", "sorting"],
      "props_info": {
        "props": [
          {
            "name": "data",
            "type": "array",
            "required": true,
            "description": "Table data array"
          },
          {
            "name": "columns",
            "type": "array",
            "required": true,
            "description": "Column definitions with width and render functions"
          },
          {
            "name": "sortable",
            "type": "boolean",
            "default": "false",
            "description": "Enable column sorting"
          },
          {
            "name": "headerStyle",
            "type": "object",
            "description": "Header styling options"
          }
        ]
      },
      "dependencies": ["react-native-gesture-handler", "react-native-reanimated"],
      "installation": "npm install react-native-gesture-handler react-native-reanimated",
      "usage_examples": [
        "<DataTable data={userData} columns={columns} sortable={true} />"
      ]
    }
  ]
}
```

**Test Navigation Bar Component:**

**Prompt:** "Search for React Native navigation bar components using MCP and show me the exact response structure."

**Expected Response:**
```json
{
  "components": [
    {
      "name": "NavigationBar",
      "description": "React Native navigation bar with header actions and drawer support",
      "platform": ["reactnative"],
      "features": ["header actions", "drawer toggle", "back button"],
      "props_info": {
        "props": [
          {
            "name": "title",
            "type": "string",
            "required": true,
            "description": "Navigation bar title"
          },
          {
            "name": "onBackPress",
            "type": "function",
            "description": "Back button press handler"
          },
          {
            "name": "rightActions",
            "type": "array",
            "description": "Right side action buttons"
          },
          {
            "name": "showDrawer",
            "type": "boolean",
            "default": "false",
            "description": "Show drawer toggle button"
          }
        ]
      },
      "dependencies": ["@react-navigation/native", "@react-navigation/stack"],
      "installation": "npm install @react-navigation/native @react-navigation/stack",
      "usage_examples": [
        "<NavigationBar title=\"Profile\" onBackPress={goBack} rightActions={[{icon: 'settings', onPress: openSettings}]} />"
      ]
    }
  ]
}
```

**Test Date Picker Component:**

**Prompt:** "Find React Native date picker components using MCP tools and show me the exact response for mobile date selection."

**Expected Response:**
```json
{
  "components": [
    {
      "name": "DatePicker",
      "description": "React Native date picker with platform-specific UI (iOS UIDatePicker, Android DatePickerDialog)",
      "platform": ["reactnative"],
      "features": ["platform specific", "modal", "range selection"],
      "props_info": {
        "props": [
          {
            "name": "value",
            "type": "Date",
            "description": "Selected date value"
          },
          {
            "name": "onChange",
            "type": "function",
            "required": true,
            "description": "Date change handler"
          },
          {
            "name": "mode",
            "type": "string",
            "default": "'date'",
            "description": "Picker mode (date, time, datetime)"
          },
          {
            "name": "minimumDate",
            "type": "Date",
            "description": "Minimum selectable date"
          },
          {
            "name": "maximumDate",
            "type": "Date",
            "description": "Maximum selectable date"
          }
        ]
      },
      "dependencies": ["@react-native-community/datetimepicker"],
      "installation": "npm install @react-native-community/datetimepicker",
      "usage_examples": [
        "<DatePicker value={selectedDate} onChange={setDate} mode=\"date\" minimumDate={new Date()} />"
      ]
    }
  ]
}
```

## Daily Usage

### Starting the System

1. **Start API Server:**
```bash
cd /Users/tbardale/v2/simflo-mcp-rag/data-pipeline
python3 api_server.py --host 127.0.0.1 --port 8000
```

2. **Verify MCP Connection:**
   - Open Claude/Cursor
   - Ask: "List available MCP tools"

### Common Workflows

**Search for Components:**
- "Find me React Native button components"
- "Search for mobile form input components"
- "Show me React Native modal components"

**Get Component Details:**
- "Tell me about the React Native TextInput component"
- "What dependencies does the mobile date picker need?"
- "Show me the navigation bar props"

**Installation Help:**
- "How do I install the React Native form component?"
- "What are the dependencies for the data table component?"

## Platform-Specific Features

### React Native Specific Props

**Layout Props:**
- `style` - StyleSheet objects instead of className
- `onPress` - Touch events instead of onClick
- `accessibilityLabel` - Screen reader support

**Input-Specific Props:**
- `keyboardType` - Mobile keyboard types
- `autoCapitalize` - Text capitalization
- `secureTextEntry` - Password input
- `placeholderTextColor` - Placeholder styling

### Mobile Considerations

**Performance:**
- Use `FlatList` for long lists instead of `map`
- Implement `memo` for component optimization
- Use `useCallback` for event handlers

**User Experience:**
- Touch target sizes (minimum 44x44 points)
- Keyboard handling with `KeyboardAvoidingView`
- Loading states and feedback

## Troubleshooting

### Server Issues

**Server Won't Start:**
```bash
# Check port 8000 is available
lsof -i :8000

# Kill any existing processes
kill -9 <PID>

# Restart server
python3 api_server.py --host 127.0.0.1 --port 8000
```

**MCP Connection Issues:**
1. Verify server is running: `curl http://127.0.0.1:8000/health`
2. Check MCP configuration paths are correct
3. Restart Claude/Cursor after configuration changes

### React Native Issues

**Empty Results:**
- Verify context: "I'm working on React Native project"
- Be specific: "React Native form components" not just "form components"

**Wrong Platform Components:**
- Explicitly mention "React Native" in queries
- Use mobile-specific terms: "TextInput" not "Input"

## Advanced Usage

### Custom Searches

**By Platform:**
- "React Native button components"
- "Expo-compatible form components"

**By Feature:**
- "Components with gesture handling"
- "Touch-friendly form components"

**By Library:**
- "Gluestack UI React Native components"
- "NativeBase mobile components"

### Platform-Specific Queries

**iOS Components:**
- "iOS-style date picker React Native"
- "Native iOS tab bar component"

**Android Components:**
- "Android material design button"
- "Android bottom navigation component"

## Integration Examples

### React Native + TypeScript Project

```typescript
import React, { useState } from 'react';
import { View, StyleSheet, Alert } from 'react-native';
import { TextInput, Button, Form } from './components';

// Ask MCP: "Show me React Native form implementation"
const LoginForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = () => {
    // Validation logic
    if (!email || !password) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    // API call logic
    console.log('Login attempt:', { email, password });
  };

  return (
    <View style={styles.container}>
      <TextInput
        label="Email"
        placeholder="Enter your email"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        autoCapitalize="none"
      />

      <TextInput
        label="Password"
        placeholder="Enter your password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />

      <Button title="Login" onPress={handleLogin} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    justifyContent: 'center',
  },
});

export default LoginForm;
```

### Navigation Integration

```typescript
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { NavigationBar } from './components';

// Ask MCP: "Show me React Native navigation setup"
const Stack = createStackNavigator();

const App = () => {
  return (
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen
          name="Home"
          component={HomeScreen}
          options={{
            header: ({ navigation }) => (
              <NavigationBar
                title="Home"
                onBackPress={navigation.goBack}
                showDrawer={true}
              />
            ),
          }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
};
```

## Performance Optimization

### Component Optimization

```typescript
import React, { memo, useCallback } from 'react';
import { TouchableOpacity, Text, StyleSheet } from 'react-native';

// Ask MCP: "Show me optimized React Native button"
interface OptimizedButtonProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary';
}

export const OptimizedButton = memo<OptimizedButtonProps>(({
  title,
  onPress,
  variant = 'primary'
}) => {
  const handlePress = useCallback(() => {
    onPress();
  }, [onPress]);

  return (
    <TouchableOpacity
      style={[
        styles.button,
        variant === 'primary' ? styles.primaryButton : styles.secondaryButton
      ]}
      onPress={handlePress}
      activeOpacity={0.7}
    >
      <Text style={styles.buttonText}>{title}</Text>
    </TouchableOpacity>
  );
});

const styles = StyleSheet.create({
  button: {
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 44,
  },
  // ... rest of styles
});
```

## Testing with MCP

### Verification Prompts

**Component Verification:**
- "Show me the exact React Native TextInput component implementation"
- "What are the mobile-specific props for the date picker?"
- "Display the complete form component with validation"

**Dependency Verification:**
- "What are all the dependencies for the React Native table component?"
- "Show me installation instructions for the navigation bar"

**Usage Verification:**
- "Show me examples of using the button component in React Native"
- "How do I implement form validation in React Native?"

This guide provides comprehensive instructions for using the SimFlo MCP RAG system with React Native projects, including platform-specific considerations and mobile-optimized component implementations.