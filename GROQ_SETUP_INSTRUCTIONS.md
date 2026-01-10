# Groq AI Setup Instructions

## ✨ What is Groq?

Groq is a **completely free** AI API with:
- ✅ **Unlimited requests** (no daily limits like OpenRouter's 50/day)
- ✅ **Fastest LLM inference** (responses in <1 second)
- ✅ **No credit card required**
- ✅ **Multiple models available**

## 🚀 Setup Steps

### Step 1: Get Your Free Groq API Key

1. Visit: https://console.groq.com/keys
2. Click "Sign Up" (takes 30 seconds)
3. Fill in your details (no credit card needed)
4. Verify your email
5. Click "Create API Key"
6. Copy the generated key

### Step 2: Add Key to `.env`

Edit your `.env` file and find this line:

```env
SUBTRACK_AI_API_KEY=
```

Paste your Groq key:

```env
SUBTRACK_AI_API_KEY=gsk_YOUR_KEY_HERE
```

Example:
```env
SUBTRACK_AI_API_KEY=gsk_abc123def456ghi789
```

### Step 3: Restart Your App

```bash
# Kill any running app (Ctrl+C in the terminal)
# Then restart:
python start.py
```

### Step 4: Test It

Visit in your browser:
```
http://localhost:8000/api/ai/test-ai-direct
```

Should return:
```json
{
  "provider_type": "GroqProvider",
  "is_available": true,
  "config": {
    "api_key": "gsk_...",
    "model": "mixtral-8x7b-32768"
  },
  "status": "success",
  "response": "..."
}
```

## 📊 Available Groq Models

All completely free and unlimited:

1. **mixtral-8x7b-32768** (Recommended - best balance)
   - Fast, intelligent, good for most tasks
   - Default model

2. **llama2-70b-4096** (Most capable)
   - Larger model, better reasoning
   - Still free and fast!

3. **gemma-7b-it** (Fastest)
   - Best for quick responses
   - Trade-off: slightly less intelligent

## 💡 How to Change Models

Edit `.env`:
```env
SUBTRACK_AI_MODEL=llama2-70b-4096
```

Then restart your app.

## ✅ Verification Checklist

- [ ] Created Groq account at https://console.groq.com
- [ ] Got API key (starts with `gsk_`)
- [ ] Added key to `.env` file
- [ ] Restarted app (`python start.py`)
- [ ] Tested endpoint: `/api/ai/test-ai-direct`
- [ ] Got successful response
- [ ] AI features working in app

## 🎉 You're All Set!

Now your SubTrack app has:
- ✅ Unlimited free AI requests
- ✅ Lightning-fast responses
- ✅ Full AI feature set working
- ✅ No rate limits or daily quotas

Start using AI features:
- Smart categorization for subscriptions
- Cost optimization suggestions
- AI-powered insights
- Link intelligence
- And more!

## 🆘 Troubleshooting

**"API Key invalid" error:**
- Check you copied the full key correctly
- Make sure key is in `.env` file
- Restart app after changing `.env`

**"Model not found" error:**
- Verify model name is spelled correctly
- Check available models above
- Default: `mixtral-8x7b-32768`

**"No response" or timeout:**
- Groq is very fast, so this is rare
- Check your internet connection
- Verify API key is valid at https://console.groq.com/keys

## 📚 Learn More

- Groq website: https://groq.com
- API docs: https://console.groq.com/docs
- Model info: https://console.groq.com/docs/models
