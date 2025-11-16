# File Serving 404 Error - Fix Documentation

## Problem Summary
Files uploaded to the server return 404 errors when accessed via `/api/files/serve/<path>`.

**Example Error:**
```
GET /api/files/serve/files/20251116_121126_fb9bfe60.png HTTP/2
< HTTP/2 404
```

## Root Cause
The `UPLOAD_FOLDER` configuration was set to `/app/src/static/files` instead of `/app/src/static`.

### How File Upload Works:
1. **File Upload**: When a file is uploaded with `subfolder='files'`:
   - Saved to: `UPLOAD_FOLDER + subfolder + filename`
   - Example: `/app/src/static/files/files/20251116_121126_fb9bfe60.png`
   - Relative path stored in DB: `files/20251116_121126_fb9bfe60.png`

2. **File URL Generation**:
   - URL: `/api/files/serve/files/20251116_121126_fb9bfe60.png`

3. **File Serving**:
   - Endpoint receives: `filename = "files/20251116_121126_fb9bfe60.png"`
   - Tries to serve from: `UPLOAD_FOLDER + filename`
   - With correct config: `/app/src/static` + `files/20251116_121126_fb9bfe60.png` = `/app/src/static/files/20251116_121126_fb9bfe60.png` ✅

### The Issue:
With `UPLOAD_FOLDER=/app/src/static/files`, the path resolution becomes:
- `/app/src/static/files` + `files/20251116_121126_fb9bfe60.png` = `/app/src/static/files/files/20251116_121126_fb9bfe60.png`

This works IF the file was saved there, BUT the configuration is inconsistent across environments.

## Changes Made

### 1. ✅ Fixed `docker-compose.yml`
```yaml
# Before:
- UPLOAD_FOLDER=/app/src/static/files

# After:
- UPLOAD_FOLDER=/app/src/static
```

### 2. ✅ Fixed `src/app.py`
```python
# Before:
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', '/app/src/static/files')

# After:
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', '/app/src/static')
```

### 3. ⚠️ Manual Changes Required - .env Files

The following .env files need to be updated manually (they are gitignored):

#### `.env` (root directory)
```bash
# Change from:
UPLOAD_FOLDER=src/static/files

# To:
UPLOAD_FOLDER=src/static
```

#### `src/.env.local`
```bash
# Change from:
UPLOAD_FOLDER=./static/files

# To:
UPLOAD_FOLDER=./static
```

#### `src/.env.production`
```bash
# Change from:
UPLOAD_FOLDER=./static/files

# To:
UPLOAD_FOLDER=./static
```

#### `src/.env.development`
```bash
# Already correct:
UPLOAD_FOLDER=/app/static/
# No change needed
```

## Deployment Steps

### For Production (Docker):
1. Update the .env files as shown above
2. Rebuild and restart the container:
   ```bash
   docker-compose --profile production down
   docker-compose --profile production build
   docker-compose --profile production up -d
   ```

### For Local Development:
1. Update `src/.env.local` as shown above
2. Restart the Flask application

## Verification

After deploying the fix, test file serving:

```bash
# Upload a file
curl -X POST https://applicationweb.datalysconsulting.com/api/files/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test.png" \
  -F "subfolder=files"

# Response will include file_url, e.g.:
# "file_url": "https://applicationweb.datalysconsulting.com/api/files/serve/files/20251116_121126_fb9bfe60.png"

# Test accessing the file
curl -I https://applicationweb.datalysconsulting.com/api/files/serve/files/20251116_121126_fb9bfe60.png
# Should return: HTTP/2 200
```

## File Structure Reference

```
/app/src/static/              ← UPLOAD_FOLDER (base directory)
├── files/                    ← subfolder for generic uploads
│   ├── 20251116_121126_fb9bfe60.png
│   └── ...
├── logos/                    ← subfolder for logo uploads
│   └── ...
├── projects/                 ← subfolder for project files
│   └── ...
└── incidents/                ← subfolder for incident files
    └── incident_123/
        └── ...
```

## Additional Notes

- The `file_upload_manager.save_file()` function automatically creates subfolders
- Subfolders are specified when calling upload endpoints (e.g., `subfolder='files'`)
- The relative path stored in the database includes the subfolder (e.g., `files/filename.png`)
- The serving endpoint `/files/serve/<path:filename>` handles the full relative path

## Related Files
- `/src/routes/files.py` - File upload and serving endpoints
- `/src/utils/file_upload.py` - FileUploadManager class
- `/src/config.py` - Configuration loading
- `/src/app.py` - Flask app initialization
- `/docker-compose.yml` - Docker configuration
