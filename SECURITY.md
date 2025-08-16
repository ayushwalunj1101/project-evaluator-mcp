# Security Policy

## 🔒 Supported Versions

We actively support the following versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | ✅ Yes             |
| < 1.0   | ❌ No              |

## 🚨 Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please follow these steps:

### 1. **Do NOT create a public issue**
Security vulnerabilities should not be reported through public GitHub issues.

### 2. **Contact us privately**
- **Email**: ayushwalunj1@gmail.com
- **Subject**: [SECURITY] Project Evaluator MCP Server Vulnerability
- **Include**: Detailed description of the vulnerability

### 3. **Provide details**
Please include as much information as possible:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if you have one)

### 4. **Response timeline**
- **Initial response**: Within 48 hours
- **Status update**: Within 7 days
- **Fix timeline**: Depends on severity (1-30 days)

## 🛡️ Security Best Practices

### For Users
1. **Keep your API keys secure**
   - Never commit API keys to version control
   - Use environment variables or .env files
   - Rotate keys regularly

2. **Use the latest version**
   - Update to the latest version regularly
   - Monitor security advisories

3. **Validate inputs**
   - Be cautious with untrusted project descriptions
   - Sanitize any user inputs

### For Contributors
1. **Code review**
   - All code changes require review
   - Security-focused review for sensitive areas

2. **Dependencies**
   - Keep dependencies updated
   - Monitor for known vulnerabilities
   - Use minimal required permissions

3. **API security**
   - Validate all API inputs
   - Use secure HTTP clients
   - Handle errors gracefully

## 🔍 Known Security Considerations

### API Key Handling
- API keys are stored in environment variables
- Keys are not logged or exposed in error messages
- Server validates key presence before operations

### Input Validation
- Project descriptions are passed to external API
- No code execution from user inputs
- Rate limiting handled by Perplexity API

### Network Security
- All API calls use HTTPS
- No sensitive data stored locally
- Minimal attack surface

## 📋 Security Checklist for Deployments

- [ ] API keys stored securely (not in code)
- [ ] Environment variables properly configured
- [ ] Latest version of dependencies installed
- [ ] Network access properly restricted
- [ ] Logging configured (without sensitive data)
- [ ] Error handling doesn't expose internals

## 🚀 Responsible Disclosure

We believe in responsible disclosure and will:

1. **Acknowledge** your report within 48 hours
2. **Investigate** the issue thoroughly
3. **Develop** a fix in coordination with you
4. **Release** the fix as soon as possible
5. **Credit** you in our security advisories (if desired)

## 📞 Contact Information

For security-related inquiries:
- **Primary**: ayushwalunj1@gmail.com
- **GitHub**: @ayushwalunj1101

Thank you for helping keep the Project Evaluator MCP Server secure! 🔒
