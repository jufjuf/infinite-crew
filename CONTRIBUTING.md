# Contributing to Infinite Crew

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/infinite-crew.git
   cd infinite-crew
   ```

3. Set up local development:
   ```bash
   cp .env.template .env
   # Edit .env with your API keys
   chmod +x scripts/local-dev.sh
   ./scripts/local-dev.sh
   ```

## Development Workflow

### Running Locally

Use Docker Compose for local development:

```bash
# Start all services
docker-compose up

# Start specific service
docker-compose up master

# View logs
docker-compose logs -f worker

# Rebuild after changes
docker-compose build worker
docker-compose up worker
```

### Testing

Run tests before submitting PRs:

```bash
# Test connections
python tests/test_connections.py

# Test decomposition
python tests/test_decomposition.py

# Run examples
python examples/simple_task.py
```

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and small

## Making Changes

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes

3. Test thoroughly:
   - Run existing tests
   - Add new tests for new features
   - Test with docker-compose locally

4. Commit with clear messages:
   ```bash
   git commit -m "feat: add priority queue support"
   ```

5. Push and create PR:
   ```bash
   git push origin feature/your-feature-name
   ```

## Pull Request Guidelines

- **Title**: Use conventional commits format (feat:, fix:, docs:, etc.)
- **Description**: Explain what and why, not how
- **Testing**: Include test results or screenshots
- **Breaking Changes**: Clearly mark if applicable

## Areas for Contribution

### High Priority

1. **Error Handling**: Improve retry logic and failure recovery
2. **Monitoring**: Add Prometheus metrics
3. **Documentation**: Expand examples and tutorials
4. **Testing**: Increase test coverage

### Feature Ideas

1. **Web UI Enhancements**:
   - Real-time task graph visualization
   - Cost tracking dashboard
   - Task templates

2. **Worker Improvements**:
   - Specialized worker types
   - Resource-aware scheduling
   - Result caching

3. **Orchestrator Features**:
   - Priority queues
   - Task dependencies
   - Conditional execution

4. **Integrations**:
   - Slack notifications
   - Webhook support
   - S3 result storage

## Architecture Decisions

When proposing significant changes:

1. Open an issue for discussion first
2. Consider backward compatibility
3. Document the rationale
4. Update ARCHITECTURE.md if needed

## Security

- Never commit API keys or secrets
- Use environment variables
- Sanitize user inputs
- Report security issues privately

## Questions?

Open an issue with the `question` label or reach out in discussions.

Thank you for contributing to Infinite Crew! 🚀