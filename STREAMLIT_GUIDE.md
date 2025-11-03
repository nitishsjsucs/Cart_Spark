# 🎨 Streamlit UI Guide

## Overview

The Clinical AI Assistant now has a beautiful, modern web interface built with Streamlit!

## 🌟 Features

### **Main Interface**
- 💬 **Chat Interface**: ChatGPT-style conversation with message bubbles
- 📚 **Source Citations Panel**: See which medical papers informed each answer
- ⚙️ **Configuration Sidebar**: Adjust model settings in real-time
- 📊 **Live Metrics**: Track query count and average response time
- 🎨 **Medical Theme**: Professional blue/white color scheme

### **Sidebar Features**
- ✅ API Key status indicator
- 🎚️ Temperature control (0.0 - 1.0)
- 📏 Max tokens slider (500 - 2000)
- 🔍 Number of sources to retrieve (3 - 15)
- 📊 Session statistics dashboard
- 🗑️ Clear chat history button
- ℹ️ About section with tech stack

### **Chat Features**
- 💬 Persistent message history
- 👤 User messages (purple gradient)
- 🤖 Assistant messages (white with border)
- ⏱️ Response time tracking
- 💡 Example questions
- 🚀 Quick submit button

### **Source Display**
- 📄 Color-coded by disease category
  - COVID-19: Red
  - Diabetes: Teal
  - Heart Attack: Orange
  - Knee Injury: Mint
- 📋 Shows disease and filename
- 🎯 Hover effects for better UX

## 🚀 Quick Start

### Method 1: PowerShell Script (Recommended)
```powershell
.\run_streamlit.ps1
```

### Method 2: Manual Launch
```powershell
streamlit run app.py
```

### Method 3: With Custom Port
```powershell
streamlit run app.py --server.port 8080
```

## 📱 Accessing the App

Once started, the app will automatically open in your browser at:
```
http://localhost:8501
```

If it doesn't open automatically, click the link shown in the terminal.

## 🎯 How to Use

### 1. **First Launch**
- The app will initialize the vector store (may take 2-3 minutes first time)
- You'll see a loading spinner: "🔄 Initializing vector store..."
- Once ready, you'll see: "✅ Vector store ready!"

### 2. **Ask Questions**
- Type your medical question in the input box
- Click "🚀 Ask" or press Enter
- Watch the assistant think and respond
- See sources cited in the right panel

### 3. **Adjust Settings**
- Use the sidebar sliders to adjust:
  - **Temperature**: Lower = more focused, Higher = more creative
  - **Max Tokens**: Control response length
  - **Number of Sources**: How many documents to retrieve

### 4. **View Statistics**
- Check the sidebar for:
  - Total queries asked
  - Average response time
  - API key status

### 5. **Clear History**
- Click "🗑️ Clear Chat History" to start fresh
- This resets the conversation and statistics

## 💡 Example Questions

Try these to get started:

1. **COVID-19**
   - "What are the symptoms of COVID-19?"
   - "How effective are machine learning models for COVID detection?"

2. **Diabetes**
   - "How to manage Type 2 diabetes with technology?"
   - "What biomarkers are important for diabetes diagnosis?"

3. **Heart Attack**
   - "What are the best predictive algorithms for heart attack detection?"
   - "How can IoT devices help in heart attack monitoring?"

4. **Knee Injury**
   - "What are the latest treatments for knee injuries?"
   - "How do exoskeletons help with knee rehabilitation?"

## 🎨 UI Components

### Color Scheme
- **Primary**: Blue (#0066cc) - Medical trust
- **Secondary**: Green (#00a86b) - Health & wellness
- **Gradients**: Purple for user, Blue-Green for headers
- **Background**: Light gray (#f8f9fa) - Easy on eyes

### Typography
- **Headers**: Bold, large, gradient backgrounds
- **Messages**: Rounded bubbles with shadows
- **Sources**: Cards with colored left borders
- **Metrics**: Large numbers with labels

### Animations
- Hover effects on source cards
- Button press animations
- Smooth transitions
- Loading spinners

## ⚙️ Configuration Options

### Temperature (0.0 - 1.0)
- **0.0**: Most deterministic, focused answers
- **0.1**: Default - slightly creative but focused
- **0.5**: Balanced creativity and focus
- **1.0**: Most creative, diverse answers

### Max Tokens (500 - 2000)
- **500**: Short, concise answers
- **1000**: Default - comprehensive answers
- **2000**: Very detailed, long-form answers

### Number of Sources (3 - 15)
- **3**: Quick answers with minimal context
- **8**: Default - balanced coverage
- **15**: Maximum context, slower but thorough

## 🔧 Troubleshooting

### App Won't Start
```powershell
# Install streamlit
pip install streamlit

# Try running directly
python -m streamlit run app.py
```

### Port Already in Use
```powershell
# Use a different port
streamlit run app.py --server.port 8502
```

### API Key Error
1. Check your `.env` file exists
2. Verify `OPENAI_API_KEY='sk-...'` is set
3. Restart the app

### Vector Store Issues
1. Delete the `chroma` folder
2. Restart the app to rebuild

### Slow Performance
1. Reduce "Number of Sources" in sidebar
2. Lower "Max Tokens" setting
3. Check your internet connection

## 📊 Performance Tips

### For Faster Responses
- Use lower number of sources (3-5)
- Reduce max tokens (500-800)
- Keep temperature at 0.1

### For Better Accuracy
- Increase number of sources (10-15)
- Use higher max tokens (1500-2000)
- Keep temperature low (0.0-0.2)

### For Balanced Performance
- Use default settings:
  - Temperature: 0.1
  - Max Tokens: 1000
  - Sources: 8

## 🎯 Advanced Features

### Session State
- Conversation history persists during session
- Statistics accumulate across queries
- Vector store loads once and stays in memory

### Responsive Design
- Works on desktop and tablet
- Two-column layout (chat + sources)
- Sidebar collapses on mobile

### Error Handling
- Graceful error messages
- Retry logic built-in
- API timeout protection

## 🚀 Deployment Options

### Local Development
```powershell
streamlit run app.py
```

### Network Access
```powershell
streamlit run app.py --server.address 0.0.0.0
```

### Production (Streamlit Cloud)
1. Push code to GitHub
2. Connect to Streamlit Cloud
3. Add secrets (OPENAI_API_KEY)
4. Deploy!

## 📝 Keyboard Shortcuts

- **Enter**: Submit question
- **Ctrl+C**: Stop server (in terminal)
- **F5**: Refresh page
- **Ctrl+Shift+R**: Hard refresh

## 🎨 Customization

### Change Colors
Edit the CSS in `app.py`:
```python
--primary-color: #0066cc;  # Change this
--secondary-color: #00a86b;  # And this
```

### Modify Layout
Adjust column ratios:
```python
col1, col2 = st.columns([2, 1])  # Change ratio
```

### Add Features
The code is modular - easy to extend with:
- Export chat history
- Save favorite responses
- Multi-language support
- Voice input/output

## 🌟 Best Practices

1. **Keep conversations focused** - Clear chat for new topics
2. **Adjust settings per use case** - Different settings for different needs
3. **Review sources** - Always check citations for accuracy
4. **Monitor metrics** - Track performance over time
5. **Report issues** - Note any errors or unexpected behavior

## 📚 Resources

- **Streamlit Docs**: https://docs.streamlit.io
- **LangChain Docs**: https://python.langchain.com
- **OpenAI API**: https://platform.openai.com/docs

## 🎉 Enjoy!

You now have a professional, production-ready medical AI assistant with a beautiful UI!

For questions or issues, check the main README.md or create an issue.
