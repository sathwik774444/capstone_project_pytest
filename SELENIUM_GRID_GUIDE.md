# Selenium Grid Setup Guide

## Configuration Overview

The project now supports both local and Selenium Grid execution modes controlled via `config.yaml`.

## Configuration Files Updated

### 1. config.yaml
```yaml
# Execution Configuration
execution:
  mode: "local"   # local or remote

# Selenium Grid Configuration
selenium_grid:
  hub_url: "http://localhost:4444/wd/hub"

# Browser Configuration
browser:
  name: "chrome"
  headless: false
  implicit_wait: 10
  explicit_wait: 30
```

### 2. docker-compose.yml
- Selenium Hub 4.21.0
- Chrome Node 4.21.0
- Firefox Node 4.21.0

## Usage Instructions

### LOCAL EXECUTION

1. **Set config.yaml:**
```yaml
execution:
  mode: "local"
```

2. **Run tests:**
```bash
pytest -v
```

### REMOTE GRID EXECUTION

1. **Set config.yaml:**
```yaml
execution:
  mode: "remote"
```

2. **Start Selenium Grid:**
```bash
docker-compose up -d
```

3. **Verify Grid Status:**
```bash
curl http://localhost:4444/status
```

4. **Run tests:**
```bash
pytest -v
```

### PARALLEL EXECUTION

For parallel test execution:

```bash
pytest -v -n 4
```

Or use pytest configuration:

```bash
pytest --dist=loadscope -v
```

## Browser Management

The `BrowserManager` class automatically:
- Detects execution mode from config
- Creates local drivers for "local" mode
- Creates remote drivers for "remote" mode
- Supports Chrome and Firefox browsers

## Grid Services

- **Hub:** http://localhost:4444
- **Console:** http://localhost:4444/grid/console
- **Status:** http://localhost:4444/status

## Cleanup

Stop Grid when done:
```bash
docker-compose down
```

## Troubleshooting

1. **Grid not accessible:**
   - Check: `docker-compose ps`
   - Restart: `docker-compose restart`

2. **Browser connection issues:**
   - Verify hub URL in config.yaml
   - Check Grid console for available nodes

3. **Test failures:**
   - Check Allure reports for detailed errors
   - Verify browser compatibility with Grid version
