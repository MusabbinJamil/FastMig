# Azure OpenAI Chat - Frontend Guide

This document describes the Azure OpenAI Chat feature in the FastMig Flutter frontend.

## Overview

The AI Chat Assistant provides a conversational interface for users to interact with their data using natural language. Users can ask questions, get analysis reports, and execute data modifications through chat.

## Accessing the Feature

1. Click the **"AI Chat"** button in the **AI Features** ribbon section
2. The chat panel opens on the right side of the screen
3. Icon: `smart_toy` (robot icon)
4. Color: Cyan

## User Interface

```
┌─────────────────────────────────────┐
│ AI Chat Assistant              [X]  │
├─────────────────────────────────────┤
│ [Summary] [Quality Report] [Recs]   │  <- Quick Actions
├─────────────────────────────────────┤
│                                     │
│ 🤖 Hello! I'm your AI Assistant...  │  <- Welcome Message
│                                     │
│ 👤 What columns have null values?   │  <- User Message
│                                     │
│ 🤖 The 'age' column has 15 missing  │  <- AI Response
│    values and 'email' has 3...      │
│                                     │
│    [Fill with Mean] [Remove Nulls]  │  <- Suggested Actions
│                                     │
├─────────────────────────────────────┤
│ [Type your message...]        [Send]│  <- Input Area
└─────────────────────────────────────┘
```

## Features

### Quick Action Chips

Three quick action buttons at the top:

| Button | Action | Description |
|--------|--------|-------------|
| **Summary** | `summary` | Get a general overview of your dataset |
| **Quality Report** | `quality_report` | Detailed data quality assessment |
| **Recommendations** | `recommendations` | AI suggestions for data improvement |

### Chat Capabilities

Users can ask questions like:
- "What columns have missing values?"
- "Describe the data types in this dataset"
- "What are the statistics for the age column?"
- "Are there any duplicate rows?"

### Data Modification Commands

Users can issue modification commands:
- "Fill missing values in age with the mean"
- "Remove duplicate rows"
- "Remove the temp_column column"
- "Convert names to uppercase"

### Suggested Actions

The AI may suggest actionable buttons that users can click to execute operations:
- **Fill with Mean** - Fill null values with column mean
- **Fill with Median** - Fill null values with column median
- **Remove Nulls** - Remove rows with null values
- **Remove Duplicates** - Remove duplicate rows

## Configuration Status

The chat panel shows the Azure OpenAI configuration status:

### Configured (Green)
- Chat is fully functional
- Input field is enabled
- All features available

### Not Configured (Orange Banner)
Shows setup instructions:
```
Azure OpenAI Not Configured

Set these environment variables in python-backend/.env:
- AZURE_OPENAI_API_KEY
- AZURE_OPENAI_ENDPOINT
- AZURE_OPENAI_DEPLOYMENT
```

### Checking (Blue)
- Shows loading spinner
- "Checking Azure OpenAI configuration..."

## File Structure

### Main Widget
**File:** `lib/widgets/azure_openai_section.dart`

```dart
class AzureOpenAISection extends StatefulWidget
class _AzureOpenAISectionState extends State<AzureOpenAISection>
class ChatMessage  // Message model
class _QuickActionChip  // Quick action button widget
```

### State Management
**File:** `lib/models/migration_data.dart`

```dart
// Feature flag
bool _enableAIChat = true;
bool get enableAIChat => _enableAIChat;
void toggleAIChat()
void setAIChat(bool value)

// API methods
Future<Map<String, dynamic>> checkOpenAIStatus()
Future<Map<String, dynamic>> sendOpenAIChat({...})
Future<Map<String, dynamic>> executeOpenAICommand(String command)
Future<Map<String, dynamic>> getOpenAIAnalysis(String analysisType)
```

### API Service
**File:** `lib/services/api_service.dart`

```dart
Future<Map<String, dynamic>> checkOpenAIStatus()
Future<Map<String, dynamic>> sendOpenAIChat({...})
Future<Map<String, dynamic>> executeOpenAICommand({...})
Future<Map<String, dynamic>> getOpenAIAnalysis({...})
```

## Integration Points

### Main Screen
**File:** `lib/screens/main_screen.dart`

```dart
// Ribbon button
_RibbonButton(
  icon: Icons.smart_toy,
  label: 'AI Chat',
  color: Colors.cyan,
  onPressed: () => _showDialog('aichat'),
  featureKey: 'aichat',
)

// Dialog mappings
case 'aichat':
  return Icons.smart_toy;      // _getDialogIcon
  return Colors.cyan;          // _getDialogColor
  return 'AI Chat Assistant';  // _getDialogTitle
  return const AzureOpenAISection();  // _getDialogContent
```

### Dev Settings Panel
**File:** `lib/widgets/dev_settings_panel.dart`

Toggle to enable/disable the AI Chat feature.

## Chat Message Model

```dart
class ChatMessage {
  final String content;
  final bool isUser;
  final DateTime timestamp;
  final List<Map<String, dynamic>>? suggestedActions;

  Map<String, dynamic> toJson() => {
    'role': isUser ? 'user' : 'assistant',
    'content': content,
  };
}
```

## Conversation History

The chat maintains conversation history for context:
- Last 10 messages are sent with each request
- History is converted to OpenAI message format
- Enables multi-turn conversations

## Error Handling

### No Data Loaded
```dart
ScaffoldMessenger.of(context).showSnackBar(
  const SnackBar(
    content: Text('Please load a dataset first to use AI features'),
    backgroundColor: Colors.orange,
  ),
);
```

### API Errors
- Error messages displayed in chat as AI responses
- User can retry their request
- Loading state properly managed

## UI Components

### Message Bubble
```dart
Container(
  padding: const EdgeInsets.all(12),
  decoration: BoxDecoration(
    color: message.isUser
        ? Colors.cyan.shade100
        : Colors.grey.shade200,
    borderRadius: BorderRadius.circular(12),
  ),
  child: SelectableText(message.content),
)
```

### Typing Indicator
Animated dots showing AI is processing:
```dart
Widget _buildTypingIndicator() {
  // Three animated dots
}
```

### Action Chips
Suggested actions from AI:
```dart
ActionChip(
  avatar: const Icon(Icons.play_arrow, size: 16),
  label: Text(_getActionLabel(action)),
  onPressed: () => _executeSuggestedAction(action),
  backgroundColor: Colors.green.shade50,
)
```

## Best Practices

### For Users
1. Load data before using AI Chat
2. Be specific in your requests
3. Use quick actions for common tasks
4. Review suggested actions before executing

### For Developers
1. Always check `_isConfigured` before enabling input
2. Handle loading states properly
3. Scroll to bottom after new messages
4. Dispose controllers in `dispose()`

## Troubleshooting

### Chat Input Disabled
- Check if Azure OpenAI is configured
- Verify backend is running
- Check network connectivity

### No Response from AI
- Check backend logs for errors
- Verify Azure OpenAI credentials
- Check if data is loaded

### Actions Not Working
- Ensure data is loaded
- Check console for errors
- Verify backend connectivity

## Dependencies

No additional Flutter packages required. Uses:
- `provider` - State management
- `http` - API calls (via ApiService)

## Related Documentation

- [Backend Integration](../../python-backend/docs/AZURE_OPENAI_INTEGRATION.md)
- [AI Features README](AI_FEATURES_README.md)
- [Dev Settings Panel](dev_settings_panel.dart)
