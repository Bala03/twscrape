# Rettiwt-API Integration Documentation

This document describes the integration of Rettiwt-API features into twscrape, providing enhanced Twitter functionality while maintaining backward compatibility.

## Overview

The Rettiwt-API integration adds advanced Twitter features to twscrape through a hybrid Python-Node.js architecture. This allows users to access features like direct messages, enhanced tweet operations, real-time streaming, and more.

## Architecture

### Hybrid System
- **Python Core**: Maintains twscrape's existing functionality and async patterns
- **Node.js Bridge**: Executes Rettiwt-API operations through subprocess calls
- **Unified API**: Single interface combining both feature sets

### Key Components
1. **RettiwtBridge**: Python-Node.js communication layer
2. **Enhanced Account Model**: Extended to store API keys and guest tokens
3. **EnhancedAPI**: Unified API class with both twscrape and Rettiwt features
4. **Database Schema**: Extended to support Rettiwt authentication data

## Authentication

Rettiwt-API supports two authentication modes:

### Guest Mode (Limited Features)
- No account required
- Auto-generated guest tokens
- Access to: tweet details, user details, user timelines, user replies

### User Mode (Full Features)
- Requires Rettiwt API key (from browser extension)
- Access to all features including: DMs, bookmarks, posting, following, etc.

## Installation & Setup

### Prerequisites
- Node.js 20+ installed
- Existing twscrape installation

### Rettiwt Dependencies
The integration automatically installs Rettiwt-API when first used:
```bash
# Dependencies are installed automatically in:
# twscrape/rettiwt_bridge_scripts/node_modules/
```

### API Key Setup (Optional)
To access full Rettiwt features, obtain an API key using browser extensions:

1. **Chrome/Edge**: Install "X Auth Helper" extension
2. **Firefox**: Install "Rettiwt Auth Helper" extension
3. Login to Twitter/X in incognito/private mode
4. Use extension to generate API key
5. Add to twscrape: `twscrape set_api_key username YOUR_API_KEY`

## New CLI Commands

### Account Management
```bash
# Set Rettiwt API key for enhanced features
twscrape set_api_key username API_KEY

# Remove API key
twscrape remove_api_key username

# Validate all stored API keys
twscrape validate_api_keys

# Show enhanced capabilities status
twscrape enhanced_capabilities
```

### Enhanced Tweet Operations
```bash
# Bookmark/unbookmark tweets (requires API key)
twscrape tweet_bookmark TWEET_ID
twscrape tweet_unbookmark TWEET_ID

# Schedule tweets (requires API key)
twscrape tweet_schedule "Tweet text" "2024-12-25T10:00:00Z"

# Access user bookmarks (requires API key)
twscrape user_bookmarks --limit 50
```

### Enhanced User Operations
```bash
# Follow/unfollow users (requires API key)
twscrape user_follow USER_ID
twscrape user_unfollow USER_ID
```

## Programming Interface

### Basic Usage
```python
from twscrape import EnhancedAPI, AccountsPool

# Initialize enhanced API
pool = AccountsPool()
api = EnhancedAPI(pool, enable_rettiwt=True)

# Check capabilities
capabilities = await api.get_enhanced_capabilities()
print(f"Rettiwt enabled: {capabilities['rettiwt_enabled']}")
print(f"Auth type: {capabilities['auth_type']}")

# Use enhanced features
result = await api.tweet_bookmark(1234567890)
async for tweet in api.user_bookmarks(limit=10):
    print(tweet.rawContent)
```

### Account Management
```python
# Set API key programmatically
success = await pool.set_api_key("username", "API_KEY")

# Validate API keys
results = await pool.validate_all_api_keys()
```

### Bridge Operations
```python
from twscrape.rettiwt_bridge import RettiwtBridge

# Direct bridge usage
bridge = RettiwtBridge(debug=True)
guest_key = await bridge.generate_guest_key()
features = await bridge.get_supported_features(api_key=None)
```

## Database Schema Changes

The integration adds new fields to the accounts table:

```sql
-- New fields in accounts table (migration v5)
ALTER TABLE accounts ADD COLUMN api_key TEXT DEFAULT NULL;
ALTER TABLE accounts ADD COLUMN api_key_valid BOOLEAN DEFAULT FALSE NOT NULL;
ALTER TABLE accounts ADD COLUMN api_key_created TEXT DEFAULT NULL;
ALTER TABLE accounts ADD COLUMN guest_key TEXT DEFAULT NULL;
```

## Feature Comparison

| Feature | twscrape | Guest Mode | User Mode |
|---------|----------|------------|-----------|
| Search tweets | ✓ | ✓ | ✓ |
| User details | ✓ | ✓ | ✓ |
| Tweet details | ✓ | ✓ | ✓ |
| User timelines | ✓ | ✓ | ✓ |
| Followers/Following | ✓ | ✗ | ✓ |
| Bookmarks | ✗ | ✗ | ✓ |
| Tweet posting | ✗ | ✗ | ✓ |
| Follow/Unfollow | ✗ | ✗ | ✓ |
| Direct Messages | ✗ | ✗ | ✓ |
| Scheduling | ✗ | ✗ | ✓ |
| Streaming | ✗ | ✗ | ✓ |

## Error Handling

### Common Issues
1. **Node.js not found**: Install Node.js 20+
2. **Network errors**: Rettiwt requires internet access to Twitter API
3. **Invalid API key**: Use browser extension to generate new key
4. **Rate limits**: Rettiwt handles rate limiting automatically

### Debug Mode
Enable debug logging for troubleshooting:
```bash
twscrape --debug enhanced_capabilities
```

```python
api = EnhancedAPI(pool, debug=True)
```

## Performance Considerations

### Memory Usage
- Node.js processes are spawned per operation
- Processes are automatically cleaned up
- Guest keys are cached per account

### Network Usage
- Rettiwt operations make direct API calls to Twitter
- No additional proxying through twscrape infrastructure
- Uses same proxy settings as configured accounts

## Backward Compatibility

- All existing twscrape commands continue to work unchanged
- Existing account data remains compatible
- Database migrations are applied automatically
- Legacy scripts require no modifications

## Security Notes

### API Key Storage
- API keys are stored in local SQLite database
- Keys are validated before storage
- Keys can be removed at any time

### Network Security
- Bridge scripts execute in isolated Node.js processes
- No persistent Node.js processes
- Temporary script files are cleaned up automatically

## Future Roadmap

### Phase 3: Additional Features
- [ ] Direct Messages: Full inbox/conversation management
- [ ] Lists: CRUD operations and timeline access
- [ ] Advanced Analytics: User insights and metrics
- [ ] Real-time Streaming: Live tweet and notification feeds

### Phase 4: Enhancements
- [ ] Bulk operations for efficiency
- [ ] Advanced filtering and search
- [ ] Media upload support
- [ ] Advanced scheduling features

## Troubleshooting

### Installation Issues
```bash
# Check Node.js installation
node --version  # Should be 20+

# Test Rettiwt installation
cd twscrape/rettiwt_bridge_scripts
npm install rettiwt-api
```

### API Key Issues
```bash
# Validate API key manually
twscrape validate_api_keys

# Check capabilities
twscrape enhanced_capabilities
```

### Debug Mode
```bash
# Enable debug output
twscrape --debug set_api_key username API_KEY
```

## Support

For issues specific to:
- **twscrape integration**: Open issue in twscrape repository
- **Rettiwt-API**: Refer to [Rettiwt-API documentation](https://rishikant181.github.io/Rettiwt-API/)
- **API key generation**: Use browser extensions as documented above