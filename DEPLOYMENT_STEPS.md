# Deployment Steps - AI Agent Integration

## Changes Made

### 1. Backend Changes (`app.py`)
- Enhanced logging to show agent URLs when configured
- Updated `/api/evaluate` endpoint to include fallback mode status in response
- Added fallback_mode, fallback_reason, and fallback_details to API response

### 2. Frontend Changes (`static/script.js`)
- Added fallback warning banner when AI agents are unavailable
- Banner shows why fallback mode is active
- Clear visual indicator (yellow warning) when using knowledge database

### 3. Configuration (`app-spec.yaml`)
- All three agent URLs properly configured
- Agent IDs correctly set
- **CRITICAL**: DIGITALOCEAN_TOKEN must be configured as a SECRET in App Platform UI

## Deployment Process

1. Push changes to git repository
2. Update App Platform configuration via `doctl`
3. Verify DIGITALOCEAN_TOKEN is configured as a secret
4. Monitor deployment logs
5. Test agent endpoints

## Expected Behavior

### With Agents Working (Normal Mode)
- AI agents process ingredient requests
- Full research capabilities
- No warning banner shown to users

### With Agents Down (Fallback Mode)
- Yellow warning banner appears
- Message: "AI agents are currently unavailable. Using knowledge-based database instead."
- Shows reason (e.g., "DIGITALOCEAN_TOKEN not configured")
- App remains functional with 17 ingredients in database

## Post-Deployment Verification

1. Check health endpoint: `https://your-app.ondigitalocean.app/api/health`
2. Verify `fallback_mode: false` in health response
3. Check `agents_online_count: 3` in health response
4. Test ingredient evaluation (e.g., "chocolate for cat")
5. Verify no warning banner appears in UI
