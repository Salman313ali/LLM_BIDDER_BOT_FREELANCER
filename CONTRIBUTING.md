# Contributing to Freelancer Bot

Thank you for your interest in contributing to the Freelancer Bot project! This document provides guidelines and information for contributors.

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Set up the development environment** (see README.md)
4. **Create a new branch** for your feature or bugfix

## 📋 Development Guidelines

### Code Style

- **Python**: Follow PEP 8 style guidelines
- **JavaScript/React**: Use ESLint configuration
- **Commit messages**: Use clear, descriptive commit messages
- **Documentation**: Update documentation for new features

### Testing

- Write tests for new functionality
- Ensure all existing tests pass
- Test both backend and frontend components
- Test with different session configurations

### Security

- Never commit API keys or sensitive data
- Use environment variables for configuration
- Follow security best practices
- Report security vulnerabilities responsibly

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Description** of the issue
2. **Steps to reproduce** the problem
3. **Expected behavior** vs actual behavior
4. **Environment details** (OS, Python version, Node.js version)
5. **Logs** and error messages
6. **Screenshots** if applicable

## ✨ Feature Requests

When requesting features, please include:

1. **Clear description** of the feature
2. **Use case** and benefits
3. **Proposed implementation** (if you have ideas)
4. **Alternative solutions** considered

## 🔧 Pull Request Process

1. **Create a feature branch** from `main`
2. **Make your changes** following the guidelines above
3. **Test thoroughly** on your local environment
4. **Update documentation** if needed
5. **Submit a pull request** with a clear description

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Manual testing completed
- [ ] No breaking changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No sensitive data committed
```

## 🏗️ Project Structure

```
freelancer-bot/
├── backend/          # FastAPI backend
├── frontend/         # React frontend
├── src/             # Core bot logic
├── tests/           # Test files
├── docs/            # Documentation
└── .github/         # GitHub workflows
```

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest tests/ -v
```

### Frontend Testing
```bash
cd frontend
npm test
```

### Integration Testing
- Test bot functionality with different configurations
- Test session management and isolation
- Test API endpoints

## 📚 Documentation

- Update README.md for significant changes
- Add inline comments for complex logic
- Update API documentation for new endpoints
- Include examples for new features

## 🔒 Security Considerations

- **API Keys**: Never commit real API keys
- **Database**: Be careful with database migrations
- **Sessions**: Ensure proper session isolation
- **Input Validation**: Validate all user inputs

## 🎯 Areas for Contribution

- **Bug fixes** and improvements
- **New features** and enhancements
- **Documentation** improvements
- **Test coverage** improvements
- **Performance** optimizations
- **Security** enhancements

## 📞 Getting Help

- **Issues**: Create an issue for bugs or questions
- **Discussions**: Use GitHub Discussions for general questions
- **Code Review**: All PRs require review before merging

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Freelancer Bot! 🎉

