# Health Chatbot Application

This project consists of a serverless chatbot backend and a React frontend for a health chatbot application designed to provide a conversational interface in the style of an Old English Village GP.

## Project Structure

```
.
├── api/
│   └── chatbot.py   # Serverless Python backend code
├── src/
│   ├── components/
│   │   ├── ChatContainer.tsx
│   │   ├── CustomScrollbar.tsx
│   │   ├── HealthChatbot.tsx
│   │   ├── InputField.tsx
│   │   ├── MessageBubble.tsx
│   │   ├── SendButton.tsx
│   │   └── ui/
│   │       ├── button.tsx
│   │       ├── card.tsx
│   │       ├── input.tsx
│   │       └── scroll-area.tsx
│   ├── App.tsx      # Main entry point for the React app
│   └── index.tsx    # React DOM render logic
├── public/
│   └── index.html
├── .env
├── .gitignore
├── package.json
├── package-lock.json
├── vercel.json      # Vercel deployment configuration
└── tsconfig.json
```

## Backend (API) Updates

The backend is located in `api/chatbot.py`. It uses a serverless handler for Vercel deployment.

### Updating the Backend Logic

- Ensure Flask and required dependencies are installed (`pip install -r requirements.txt`), though for Vercel, the code is using `BaseHTTPRequestHandler`.
- Maintain the existing route (`/api/chatbot`) unless you're also updating the frontend to match.
- Keep the conversation dictionary up to date to enhance the chatbot's responses.

Example of updating the chatbot logic:

```python
# Helper function to find best match
def find_best_match(user_input, state):
    # Update your chatbot logic here
    ...
```

## Frontend Updates

The frontend is a React application using TypeScript.

### Updating the Frontend Components

- The main application logic is in `src/App.tsx` and components are in `src/components/`.
- Ensure all dependencies are installed (`npm install`).
- Maintain the structure of `App.tsx` unless you're refactoring the entire application.
- When updating or adding components, keep them in the `src/components/` directory.

Example of updating a component:

```tsx
// src/components/HealthChatbot.tsx
import React, { useState } from 'react';
import { Card } from './ui/card';
import { Input } from './ui/input';
import { Button } from './ui/button';

const HealthChatbot: React.FC = () => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<string[]>([]);

  const handleSend = async () => {
    // Update API call logic here
    const response = await fetch('/api/chatbot', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ input }),
    });
    const data = await response.json();
    setMessages([...messages, `You: ${input}`, `Bot: ${data.response}`]);
    setInput('');
  };

  return (
    <Card>
      {/* Update UI components here */}
    </Card>
  );
};

export default HealthChatbot;
```

## Development Workflow

1. Use your preferred external editor to make changes.
2. **Backend Changes**:
   - Run the server locally (`python api/chatbot.py`).
   - Test endpoints using tools like Postman or curl.
3. **Frontend Changes**:
   - Run the React development server (`npm start`).
   - Test in the browser (usually at [http://localhost:3000](http://localhost:3000)).
4. Commit changes frequently and use descriptive commit messages.
5. **Deployment**:
   - Ensure `vercel.json` is correctly set up for deployment.
   - Run `vercel` to deploy both backend and frontend.

## Vercel Configuration

The `vercel.json` file is used to define the deployment settings for both the backend and frontend.

```json
{
  "builds": [
    {
      "src": "api/**/*.py",
      "use": "@vercel/python"
    },
    {
      "src": "src/**/*",
      "use": "@vercel/node"
    },
    {
      "src": "public/**/*",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/api/chatbot",
      "dest": "api/chatbot.py"
    },
    {
      "src": "/(.*)",
      "dest": "public/index.html"
    }
  ]
}
```

By following these guidelines, you can safely update both the backend logic and the frontend interface without breaking existing functionality, and deploy the updated version to Vercel for production.

### Common Deployment Errors

- **JSON Parsing Error**: Make sure the `package.json` and `vercel.json` files are correctly formatted. Common issues include missing commas, incorrect quotes, or misplaced braces.
- **Push Issues**: Ensure all changes are committed and pushed to the correct upstream branch (`git push --set-upstream origin main` if needed).

# eas
