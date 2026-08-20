# Security Policy

## Overview

MindGuardian AI prioritizes **security** and **privacy** as core requirements. This document outlines our security practices and vulnerability disclosure process.

---

## Security Principles

1. **Privacy-First Architecture**
   - Minimal data collection
   - Local-first processing
   - User data sovereignty
   - Transparent data usage

2. **Defense in Depth**
   - Multiple security layers
   - No single point of failure
   - Graceful degradation

3. **Security by Design**
   - Security integrated from the start
   - Regular threat modeling
   - Secure defaults

4. **Transparency**
   - Clear privacy policy
   - Open source code
   - Public security reviews

---

## Supported Versions

| Version | Status | Support Until |
|---------|--------|---------------|
| 1.x | Current | Ongoing |
| 0.x | EOL | 2026-08-01 |

**Security updates**: Released ASAP, separate from feature releases

---

## Vulnerability Disclosure

### Responsible Disclosure Process

**DO NOT** open public GitHub issues for security vulnerabilities.

#### Step 1: Report
Email security details to: `[Open issue on GitHub for contact info]`

**Include:**
- Type of vulnerability
- Location (file, component)
- Impact assessment
- Reproduction steps
- Proof of concept (if safe to share)

#### Step 2: Review
- Response within 48 hours
- Severity assessment
- Fix timeline discussed

#### Step 3: Fix
- We will work to fix the issue
- Timeline: 7-30 days depending on severity

#### Step 4: Disclosure
- Fix released in security update
- You credited in release notes
- Public disclosure 30 days after release (unless earlier agreement)

### Severity Classification

| Severity | Impact | Timeline |
|----------|--------|----------|
| **Critical** | Data leakage, RCE, auth bypass | 24-48 hours |
| **High** | Significant privacy/security impact | 7 days |
| **Medium** | Moderate risk, workaround available | 14 days |
| **Low** | Minor issue, cosmetic/limited impact | 30 days |

---

## Security Features

### Authentication & Authorization

- ✅ **JWT Tokens**: RS256 asymmetric signing
- ✅ **Password Security**: bcrypt hashing (12+ rounds)
- ✅ **Session Management**: Stateless, token-based
- ✅ **Rate Limiting**: Prevent brute force attacks
- ✅ **RBAC**: Role-based access control
- ✅ **MFA Ready**: Architecture supports 2FA (future)

### Data Protection

- ✅ **Encryption in Transit**: HTTPS/TLS 1.3
- ✅ **Encryption at Rest**: AES-256 (optional, configurable)
- ✅ **Database Security**:
  - SQL injection prevention (SQLAlchemy ORM)
  - Input validation (Pydantic)
  - Parameterized queries
- ✅ **Secret Management**: Environment variables, no hardcoded secrets

### API Security

- ✅ **CORS Configuration**: Whitelist-based
- ✅ **Input Validation**: Pydantic schema validation
- ✅ **Error Handling**: No sensitive info in error messages
- ✅ **API Rate Limiting**: 100 req/min per user (configurable)
- ✅ **API Versioning**: `/api/v1/` format for forward compatibility

### Frontend Security

- ✅ **XSS Prevention**: No innerHTML, content sanitization
- ✅ **CSRF Protection**: Token-based (if using cookies)
- ✅ **Local Storage**: No sensitive data stored permanently
- ✅ **CSP Headers**: Content Security Policy configured

### Privacy Protections

- ✅ **No Cloud Dependencies**: Works offline
- ✅ **Local Processing**: Video/audio not sent to servers
- ✅ **Data Minimization**: Only necessary features extracted
- ✅ **User Control**: Delete data on demand
- ✅ **Audit Logging**: Track data access
- ✅ **Data Export**: GDPR compliance (data portability)

---

## Security Testing

### Regular Audits

- Monthly: Automated security scanning (Bandit, OWASP)
- Quarterly: Manual code review by security team
- Annually: Third-party penetration testing

### Dependency Management

```bash
# Check for known vulnerabilities
safety check

# Update dependencies safely
pip-audit

# Lock versions
pip-compile requirements.in -o requirements.txt
```

### CI/CD Security

- ✅ Secret scanning in commits
- ✅ SAST (Static Application Security Testing)
- ✅ Dependency vulnerability checks
- ✅ Container image scanning

---

## Incident Response

### If You Suspect a Breach

1. **Do Not Panic**: React calmly and systematically
2. **Notify Maintainers**: Email security contact immediately
3. **Preserve Evidence**: Don't modify logs/data
4. **Limit Exposure**: Stop using compromised credentials
5. **Document**: Keep timeline of events

### Our Response

1. **Investigate**: Determine scope and impact
2. **Contain**: Limit damage, prevent further access
3. **Communicate**: Notify affected users
4. **Remediate**: Fix root cause
5. **Review**: Post-mortem, improve processes

---

## Compliance

### Standards & Frameworks

- 🔒 **OWASP Top 10**: Addressed in architecture
- 🔒 **GDPR**: Data privacy regulations (EU)
- 🔒 **CCPA**: Consumer privacy (California)
- 🔒 **HIPAA Ready**: Architecture supports healthcare compliance
- 🔒 **SOC 2**: Control framework documented

### Privacy Policy

See `PRIVACY.md` for detailed privacy practices.

---

## Security Best Practices for Users

### For End Users

1. **Use Strong Passwords**
   - 12+ characters
   - Mix of uppercase, lowercase, numbers, symbols
   - Unique for each account

2. **Protect Your Token**
   - Never share your JWT token
   - Clear browser storage when done
   - Use private/incognito mode on shared computers

3. **Keep Software Updated**
   - Update browser regularly
   - Update MindGuardian when updates available
   - Keep OS patched

4. **Use HTTPS Only**
   - Always connect via HTTPS
   - Check padlock icon in address bar
   - Avoid unsecured WiFi

### For Developers

1. **Code Review**
   - Review all security-related changes
   - Use static analysis tools
   - Test edge cases

2. **Dependency Updates**
   - Keep dependencies current
   - Monitor security advisories
   - Use lock files for reproducibility

3. **Secrets Management**
   - Never commit secrets
   - Use environment variables
   - Rotate keys regularly

4. **Logging**
   - Don't log sensitive data
   - Use centralized logging
   - Monitor for suspicious activity

---

## Security Roadmap

### Near Term (3 months)
- [ ] Add rate limiting to all APIs
- [ ] Implement CORS policy
- [ ] Security audit of vision pipeline
- [ ] Update dependencies

### Medium Term (6 months)
- [ ] Add 2FA support
- [ ] Implement data encryption at rest
- [ ] Third-party penetration test
- [ ] Security documentation

### Long Term (12 months)
- [ ] HIPAA compliance certification
- [ ] Bug bounty program
- [ ] Formal threat modeling
- [ ] ISO 27001 alignment

---

## Resources

- **OWASP**: https://owasp.org
- **CWE Top 25**: https://cwe.mitre.org/top25
- **NIST Cybersecurity Framework**: https://nist.gov/cyberframework
- **PortSwigger Web Security**: https://portswigger.net/web-security

---

## Questions?

For security questions or to report vulnerabilities, open an issue on GitHub.

---

**Last Updated**: 2026-08-20
**Next Review**: 2026-11-20
