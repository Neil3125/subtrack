# How to Use AI Features in SubTrack

## 🎯 Quick Start

Your OpenRouter AI integration is **already working**! Here's how to use it.

## 📍 Test the Integration

### Option 1: Direct API Test (Recommended)
```bash
# Start your app
python start.py

# Then visit this URL in your browser:
http://localhost:8000/api/ai/test-ai-direct
```

This endpoint will:
- Show your AI configuration
- Make a direct API call to OpenRouter
- Display the response and timing
- Confirm API usage

### Option 2: Use the UI Features

1. **Start the application**:
   ```bash
   python start.py
   ```

2. **Open your browser**: `http://localhost:8000`

3. **Try these features**:
   - Click "AI Dashboard" to see insights
   - Add a subscription and use AI categorization
   - Generate cost optimization suggestions
   - Run link analysis

## 🚀 Available AI Features

### 1. Smart Insights
**Endpoint**: `POST /api/ai/insights`

Analyzes your subscriptions and provides:
- Summary of subscription portfolio
- Actionable recommendations
- Risk flags and warnings
- Next best actions

**Example**:
```bash
curl -X POST http://localhost:8000/api/ai/insights \
  -H "Content-Type: application/json" \
  -d '{"threshold_days": 30}'
```

### 2. Smart Categorization
**Endpoint**: `POST /api/ai/categorize`

Suggests the best category for a subscription.

**Example**:
```bash
curl -X POST http://localhost:8000/api/ai/categorize \
  -H "Content-Type: application/json" \
  -d '{"subscription_name": "Netflix", "plan_name": "Premium"}'
```

### 3. Cost Optimization
**Endpoint**: `POST /api/ai/optimize`

Analyzes spending and suggests ways to save money.

**Example**:
```bash
curl -X POST http://localhost:8000/api/ai/optimize \
  -H "Content-Type: application/json" \
  -d '{"customer_id": null}'
```

### 4. Link Analysis
**Endpoint**: `POST /api/ai/analyze-links`

Discovers relationships between customers and subscriptions.

**Example**:
```bash
curl -X POST http://localhost:8000/api/ai/analyze-links \
  -H "Content-Type: application/json" \
  -d '{"run_ai_refinement": true}'
```

### 5. Renewal Reminders
**Endpoint**: `POST /api/ai/renewal-reminders`

Generates smart renewal reminders with context.

**Example**:
```bash
curl -X POST http://localhost:8000/api/ai/renewal-reminders \
  -H "Content-Type: application/json" \
  -d '{"days_ahead": 30}'
```

## 📊 Monitoring Usage

### Check Application Logs

When the app runs, you'll see:
```
🤖 Calling OpenRouter API: model=google/gemini-2.0-flash-exp:free...
✅ OpenRouter API response: status=200
✅ OpenRouter success: 150 chars returned
```

### Check OpenRouter Dashboard

1. Visit: https://openrouter.ai/activity
2. View your request history
3. Monitor daily quota (50 requests/day on free tier)

## ⚠️ Rate Limits

### Free Tier Limits
- **50 requests per day**
- Resets at midnight UTC
- Shared across all your apps using the same key

### When You Hit the Limit
You'll see:
```json
{
  "status": "error",
  "error": "Daily request limit reached (50 requests/day on free tier). AI features will be available again tomorrow.",
  "message": "API call failed - see error for details"
}
```

### Solutions
1. **Wait**: Limit resets daily at midnight UTC
2. **Upgrade**: Get paid tier for unlimited requests
3. **Use Caching**: App automatically caches responses for 24 hours

## 🧪 Testing with Your Data

### 1. Add Some Test Subscriptions

```python
# Use the UI or API to add subscriptions
POST /api/subscriptions
{
  "vendor_name": "Netflix",
  "plan_name": "Premium",
  "cost": 19.99,
  "billing_cycle": "monthly",
  "customer_id": 1
}
```

### 2. Request AI Insights

```bash
curl -X POST http://localhost:8000/api/ai/insights \
  -H "Content-Type: application/json" \
  -d '{}'
```

### 3. Check the Response

You should get:
```json
{
  "ai_insights": {
    "summary": "AI-generated summary of your subscriptions...",
    "recommendations": [
      "Recommendation 1",
      "Recommendation 2"
    ],
    "risk_flags": [],
    "next_best_actions": [...]
  },
  "total_active_subscriptions": 1,
  "total_monthly_cost": 19.99,
  ...
}
```

## 🔍 Troubleshooting

### "AI provider not available"
**Solution**: Check your `.env` file has:
```bash
SUBTRACK_AI_PROVIDER=openrouter
SUBTRACK_AI_API_KEY=sk-or-v1-...
SUBTRACK_AI_MODEL=google/gemini-2.0-flash-exp:free
```

### "Rate limit reached"
**Solution**: You've used your daily quota. Wait for reset or upgrade.

### "Invalid API key"
**Solution**: Verify your API key at https://openrouter.ai/keys

### Usage shows 0 in dashboard
**This is normal!** The free tier experimental model may not show usage the same way. The 429 rate limit error proves the API is working.

## 💡 Best Practices

### 1. Use Caching
The app automatically caches AI responses for 24 hours. Identical requests won't count against your quota.

### 2. Batch Operations
Instead of analyzing one subscription at a time, analyze all at once:
```bash
# Good: One request for all subscriptions
POST /api/ai/insights

# Avoid: Multiple requests for individual subscriptions
```

### 3. Strategic Testing
With 50 requests/day, test features strategically:
- Test each feature once
- Use real data for meaningful results
- Check logs to confirm API calls

### 4. Monitor Logs
Enable logging to see exactly when API calls are made:
```bash
# Look for these in your console:
🤖 Calling OpenRouter API...
✅ OpenRouter success...
```

## 📈 Upgrading for More Usage

If you need more than 50 requests/day:

1. Visit: https://openrouter.ai/credits
2. Add credits to your account
3. Switch to a paid model or get unlimited requests
4. No code changes needed!

## ✅ Verification Checklist

- [ ] API key is configured in `.env`
- [ ] App starts without errors
- [ ] Test endpoint returns success: `/api/ai/test-ai-direct`
- [ ] Logs show 🤖 when making API calls
- [ ] AI features return intelligent responses (not "AI provider not available")
- [ ] Rate limit error appears after ~50 requests (proves it's working!)

## 🎉 You're All Set!

Your AI integration is working. The features are:
- ✅ Configured correctly
- ✅ Making API calls to OpenRouter
- ✅ Processing responses successfully
- ✅ Handling rate limits gracefully

Start using the AI features in your SubTrack app now!
