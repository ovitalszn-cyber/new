# KashRock API - API Key Management

## Quick Start

### 1. Generate Initial API Keys

```bash
cd KashRockAPI
python generate_api_keys.py
```

This creates 5 test API keys:
- **tester_1**: Primary tester (1000 req/hour, 30 days)
- **tester_2**: Secondary tester (1000 req/hour, 30 days)  
- **tester_3**: Limited access (500 req/hour, 7 days)
- **admin**: Admin access (10000 req/hour, never expires)
- **demo**: Demo access (100 req/hour, 24 hours)

### 2. Generate Custom API Keys

```bash
# Generate single key
python generate_api_keys.py tester_4

# Generate custom key with specific limits
python generate_api_keys.py vip_user 2000 60
```

### 3. Test API Keys

```bash
# Test with generated key
curl -s 'https://kashrock-api.onrender.com/health' \
  -H 'Authorization: Bearer kr_Ryb2qp6GnaTRU7kmW-RZBPaJd292f1QhD8PX8FdaL8o'

# Test odds endpoint
curl -s 'https://kashrock-api.onrender.com/v1/odds/upcoming?sport=football_nfl&books=prophetx' \
  -H 'Authorization: Bearer kr_Ryb2qp6GnaTRU7kmW-RZBPaJd292f1QhD8PX8FdaL8o' | jq
```

## Admin Management

### List All API Keys

```bash
curl -s 'https://kashrock-api.onrender.com/admin/keys' \
  -H 'Authorization: Bearer ADMIN_KEY_HERE' | jq
```

### Generate New Key via API

```bash
curl -s -X POST 'https://kashrock-api.onrender.com/admin/keys/generate?name=new_tester&rate_limit=1000&expires_days=30' \
  -H 'Authorization: Bearer ADMIN_KEY_HERE' | jq
```

## API Key Types

| Type | Rate Limit | Expiry | Use Case |
|------|------------|--------|----------|
| **admin** | 10,000/hour | Never | Full access, key management |
| **tester_1/2** | 1,000/hour | 30 days | Primary testers |
| **tester_3** | 500/hour | 7 days | Limited testing |
| **demo** | 100/hour | 24 hours | Quick demos |

## Security Notes

- **Never commit API keys to git**
- **Use environment variables in production**
- **Rotate keys regularly**
- **Monitor usage patterns**
- **Deactivate unused keys**

## Environment Variables (Production)

Set these in your Render dashboard:

```bash
# Admin key (for key management)
ADMIN_API_KEY=kr_Ioipxhz1jG1wuhnRElopGdLTQSSm_jNBe_hY0AoZlVA

# Additional test keys
API_KEY_1=tester_1:kr_Ryb2qp6GnaTRU7kmW-RZBPaJd292f1QhD8PX8FdaL8o:active:1000
API_KEY_2=tester_2:kr_nGwqr3TRW0iZGxNZ9FTPzIPu_famHL-XYfjPoN6e518:active:1000
API_KEY_3=tester_3:kr_9lopFxtXTJ443jMNVElm8u2UPlwCO_hx-YcglghB5f8:active:500
```

## Key Format

API keys follow this format:
```
kr_[32-character-random-string]
```

Example: `kr_Ryb2qp6GnaTRU7kmW-RZBPaJd292f1QhD8PX8FdaL8o`

## Distribution to Testers

Send testers:
1. **API Key**: `kr_Ryb2qp6GnaTRU7kmW-RZBPaJd292f1QhD8PX8FdaL8o`
2. **Base URL**: `https://kashrock-api.onrender.com`
3. **Documentation**: Link to README.md
4. **Rate Limit**: 1000 requests/hour
5. **Expiry**: 30 days

## Monitoring

Check key usage:
```bash
curl -s 'https://kashrock-api.onrender.com/admin/keys' \
  -H 'Authorization: Bearer ADMIN_KEY' | jq '.[] | {name, usage_count, last_used}'
```

## Troubleshooting

- **401 Unauthorized**: Check API key format and validity
- **403 Forbidden**: Admin endpoint requires admin key
- **Rate Limited**: Wait for rate limit reset (hourly)
- **Key Expired**: Generate new key or extend expiry
