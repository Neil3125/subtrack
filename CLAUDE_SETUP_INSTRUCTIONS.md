# Claude AI Setup Instructions

## ✨ Why Claude?

Claude is the best choice because:
- ✅ **No organization account needed** (just personal account)
- ✅ **Super intelligent** (better responses than Llama/Mistral)
- ✅ **Pay-as-you-go** (very cheap - $3 per 1 million input tokens)
- ✅ **Free $5 trial credit** to start
- ✅ **No credit card required** for trial

## 💰 Pricing (Extremely Cheap)

Claude 3.5 Sonnet (recommended):
- **Input**: $3 per million tokens (~500 pages of text)
- **Output**: $15 per million tokens

With $5 free trial credit, you could run **thousands** of AI analyses for free!

## 🚀 Setup Steps (2 minutes)

### Step 1: Create Anthropic Account

1. Visit: https://console.anthropic.com/
2. Click "Sign Up"
3. Use your email (no organization needed!)
4. Verify email
5. Accept terms

### Step 2: Get Your API Key

1. In console, go to **API Keys** section
2. Click "Create Key"
3. Name it "SubTrack"
4. Copy the key (starts with `sk-ant-`)

### Step 3: Add Key to `.env`

Edit `.env` file and find:

```env
SUBTRACK_AI_API_KEY=
```

Paste your key:

```env
SUBTRACK_AI_API_KEY=sk-ant-YOUR_KEY_HERE
```

Example:
```env
SUBTRACK_AI_API_KEY=sk-ant-v0-abc123def456
```

### Step 4: Restart Your App

```bash
# Kill running app (Ctrl+C)
# Then restart:
python start.py
```

### Step 5: Test It

Visit in your browser:
```
http://localhost:8000/api/ai/test-ai-direct
```

Should return:
```json
{
  "provider_type": "AnthropicProvider",
  "is_available": true,
  "config": {
    "api_key": "sk-ant-...",
    "model": "claude-3-5-sonnet-20241022"
  },
  "status": "success",
  "response": "..."
}
```

## 📊 Available Claude Models

All available for the same cheap price:

1. **claude-3-5-sonnet-20241022** (Recommended - best balance)
   - Fast, intelligent, best for most tasks
   - Default model

2. **claude-3-opus-20240229** (Most capable)
   - Larger model, better reasoning
   - Slower but more accurate
   - Great for complex analysis

3. **claude-3-haiku-20240307** (Fastest & cheapest)
   - Smallest model, fastest responses
   - Perfect for quick categorization

## 🔧 How to Change Models

Edit `.env`:
```env
SUBTRACK_AI_MODEL=claude-3-opus-20240229
```

Then restart your app.

## 💳 Billing

- **Free tier**: $5 credit (no credit card required initially)
- **After free tier**: Pay-as-you-go (only charge when you use it)
- **No minimum spend** or subscription
- **Very transparent** - see exact costs in dashboard

## ✅ Verification Checklist

- [ ] Created account at https://console.anthropic.com/
- [ ] Got API key (starts with `sk-ant-`)
- [ ] Added key to `.env` file
- [ ] Restarted app (`python start.py`)
- [ ] Tested endpoint: `/api/ai/test-ai-direct`
- [ ] Got successful response
- [ ] AI features working in app

## 🎉 You're All Set!

Now your SubTrack app has:
- ✅ Powerful AI (Claude)
- ✅ Very cheap ($3 per million tokens)
- ✅ $5 free credit to start
- ✅ Full AI feature set working
- ✅ Full AI categorization, insights, optimization

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
- Verify key starts with `sk-ant-`

**"Model not found" error:**
- Verify model name is spelled correctly
- Check available models above
- Default: `claude-3-5-sonnet-20241022`

**"Billing issue" error:**
- You likely used up your $5 free credit
- Add payment method in console
- Set usage limits if desired

## 📚 Learn More

- Anthropic website: https://www.anthropic.com
- API docs: https://docs.anthropic.com
- Console: https://console.anthropic.com/
- Pricing: https://www.anthropic.com/pricing

## 💡 Pro Tips

1. **Use the free $5 credit** - Test everything you want for free!
2. **Monitor costs** - Dashboard shows exact API usage
3. **Set spending limits** - Prevent unexpected charges
4. **Use Haiku for quick tasks** - Save money on simple categorization
5. **Use Sonnet for complex analysis** - Better results for insights

You can literally run thousands of AI requests with the $5 free credit!
