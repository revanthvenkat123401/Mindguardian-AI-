# Testing Standards & Quality Assurance

## Overview

MindGuardian AI follows rigorous testing standards to ensure:
- ✅ **Reliability**: Code works as intended
- ✅ **Safety**: No data leaks or privacy violations
- ✅ **Accuracy**: AI models perform as documented
- ✅ **Reproducibility**: Results can be verified independently

---

## Test Categories

### 1. Unit Tests

**Purpose**: Test individual functions/components in isolation

**Requirements:**
- One test per logical condition
- Clear test names describing what is tested
- Arrange-Act-Assert pattern
- Mock external dependencies

**Example:**
```python
def test_calculate_burnout_risk_with_valid_metrics():
    """Test burnout risk calculation with normal input."""
    # Arrange
    metrics = {
        'fatigue': 0.6,
        'stress': 0.4,
        'engagement': 0.3
    }
    
    # Act
    risk = calculate_burnout_risk(metrics)
    
    # Assert
    assert 0 <= risk <= 1
    assert risk > 0.5  # Should indicate elevated risk

def test_calculate_burnout_risk_with_missing_metrics():
    """Test error handling for missing metrics."""
    # Arrange
    metrics = {'fatigue': 0.6}  # Missing stress, engagement
    
    # Act & Assert
    with pytest.raises(ValueError):
        calculate_burnout_risk(metrics)
```

**Coverage Targets:**
```
Backend: ≥ 80% overall
  - AI Pipeline: ≥ 90%
  - Auth/Security: 100%
  - Database: ≥ 85%
  - APIs: ≥ 80%

Frontend: ≥ 70%
  - Core functionality: ≥ 80%
  - UI components: ≥ 60%
```

### 2. Integration Tests

**Purpose**: Test components working together

**Requirements:**
- Test real database (test DB)
- Test API endpoints end-to-end
- Test authentication flow
- Mock external services

**Test Cases:**
```python
class TestSessionWorkflow:
    """Test complete session creation and monitoring workflow."""
    
    def test_create_session_and_ingest_metrics(self, client, test_user):
        """User can create session and send metrics."""
        # Create session
        response = client.post(
            '/api/v1/sessions/start',
            json={'title': 'Test', 'activity_type': 'coding'},
            headers=test_user.auth_headers
        )
        assert response.status_code == 201
        session_id = response.json()['id']
        
        # Send metrics
        metrics = {'cognitive_load': 0.7, 'stress': 0.4}
        response = client.post(
            f'/api/v1/sessions/{session_id}/metrics',
            json=metrics,
            headers=test_user.auth_headers
        )
        assert response.status_code == 200
        
        # Verify metrics stored
        response = client.get(
            f'/api/v1/sessions/{session_id}',
            headers=test_user.auth_headers
        )
        assert response.json()['avg_cognitive_load'] == 0.7
```

### 3. AI/ML Model Tests

**Purpose**: Validate ML model performance and reproducibility

**Test Structure:**
```python
class TestCognitiveLoadModel:
    """Test cognitive load prediction model."""
    
    def test_model_output_range(self):
        """Model output should be in [0, 1] range."""
        model = CognitiveLoadModel.load()
        features = generate_test_features()
        output = model.predict(features)
        assert 0 <= output <= 1
    
    def test_model_consistency(self):
        """Same input should produce same output."""
        model = CognitiveLoadModel.load()
        features = generate_test_features()
        
        output1 = model.predict(features)
        output2 = model.predict(features)
        
        assert output1 == output2
    
    def test_model_sensitivity_analysis(self):
        """Model should respond reasonably to input changes."""
        model = CognitiveLoadModel.load()
        features = generate_test_features()
        
        # Baseline
        baseline = model.predict(features)
        
        # Increase fatigue by 20%
        features['fatigue'] *= 1.2
        increased = model.predict(features)
        
        # Should increase but not drastically
        assert increased > baseline
        assert increased - baseline < 0.3  # Max 30% change
    
    def test_model_edge_cases(self):
        """Test extreme input values."""
        model = CognitiveLoadModel.load()
        
        # All zeros
        features = {k: 0 for k in feature_names}
        output = model.predict(features)
        assert 0 <= output <= 1
        
        # All ones
        features = {k: 1 for k in feature_names}
        output = model.predict(features)
        assert 0 <= output <= 1
```

### 4. Privacy & Security Tests

**Purpose**: Ensure no data leaks or vulnerabilities

**Critical Tests:**
```python
class TestPrivacyCompliance:
    """Test privacy requirements are met."""
    
    def test_no_raw_video_stored(self, db):
        """Verify raw video frames never stored in database."""
        # Send session with video
        session = create_test_session()
        
        # Check database
        stored_data = db.query(SessionData).filter_by(
            session_id=session.id
        ).all()
        
        for record in stored_data:
            assert 'raw_frame' not in record.data
            assert 'video_blob' not in record.data
            assert 'base64_image' not in record.data
    
    def test_data_encryption_at_rest(self, db):
        """Verify sensitive data encrypted in database."""
        metrics = create_test_metrics()
        session = create_test_session()
        
        # Store metrics
        db.add_session_metrics(session.id, metrics)
        
        # Query raw database
        raw_record = db.session.execute(
            "SELECT * FROM session_metrics WHERE session_id = %s",
            (session.id,)
        ).fetchone()
        
        # Should not contain plaintext sensitive data
        assert 'base64' not in str(raw_record)
        assert metrics['cognitive_load'] not in str(raw_record)
    
    def test_jwt_token_expiration(self, client, test_user):
        """Verify JWT tokens expire correctly."""
        # Get token
        response = client.post(
            '/api/v1/users/login',
            json=test_user.credentials
        )
        token = response.json()['access_token']
        
        # Try to use after expiration
        with freeze_time('2026-09-01 01:00'):
            response = client.get(
                '/api/v1/users/me',
                headers={'Authorization': f'Bearer {token}'}
            )
            assert response.status_code == 401
    
    def test_no_password_leakage(self, db, test_user):
        """Verify passwords never logged or exposed."""
        # Perform login
        password = test_user.password
        
        # Check logs
        logs = get_recent_logs()
        for log_entry in logs:
            assert password not in log_entry
            assert test_user.username not in log_entry.get('password', '')
        
        # Check database
        user_record = db.query(User).filter_by(
            username=test_user.username
        ).first()
        assert user_record.hashed_password != password
        # bcrypt should be used
        assert user_record.hashed_password.startswith('$2')
```

### 5. Performance Tests

**Purpose**: Ensure acceptable latency and resource usage

**Benchmarks:**
```python
class TestPerformance:
    """Test system performance meets requirements."""
    
    def test_vision_pipeline_latency(self, benchmark):
        """Vision pipeline should process frame in <100ms."""
        frame = generate_test_frame()
        
        def process_frame():
            return process_vision_frame(frame)
        
        result = benchmark(process_frame)
        assert result.stats.mean < 0.1  # 100ms
    
    def test_metrics_ingestion_throughput(self, benchmark):
        """Should handle 10+ metrics/second per user."""
        session = create_test_session()
        metrics_batch = [generate_test_metrics() for _ in range(100)]
        
        def ingest_metrics():
            return api.ingest_metrics(session.id, metrics_batch)
        
        result = benchmark(ingest_metrics)
        assert result.stats.mean < 10  # 100 metrics in <10s = 10+/s
    
    def test_memory_usage_during_session(self):
        """Memory shouldn't grow unbounded during session."""
        import tracemalloc
        tracemalloc.start()
        
        session = create_test_session()
        
        # Simulate 1 hour of metrics (60 per minute)
        start = tracemalloc.get_traced_memory()[0]
        
        for i in range(3600):
            metrics = generate_test_metrics()
            api.ingest_metrics(session.id, metrics)
        
        end = tracemalloc.get_traced_memory()[0]
        memory_increase_mb = (end - start) / 1024 / 1024
        
        assert memory_increase_mb < 100  # Less than 100MB increase
```

### 6. Reproducibility Tests

**Purpose**: Ensure research results can be verified

**Protocol:**
```python
class TestReproducibility:
    """Test that results are reproducible."""
    
    def test_model_determinism(self):
        """Model should produce identical results with seed."""
        seed = 42
        features = generate_test_features()
        
        # Run 1
        np.random.seed(seed)
        model1 = train_model(features)
        output1 = model1.predict(features)
        
        # Run 2
        np.random.seed(seed)
        model2 = train_model(features)
        output2 = model2.predict(features)
        
        assert np.allclose(output1, output2)
    
    def test_results_documented(self):
        """All results should have metadata."""
        results = run_experiment()
        
        required_fields = [
            'timestamp', 'seed', 'data_version',
            'model_version', 'hyperparameters',
            'metrics', 'confidence_intervals'
        ]
        
        for field in required_fields:
            assert field in results
            assert results[field] is not None
```

---

## Running Tests

### Local Development

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=backend --cov-report=html

# Specific test file
pytest tests/test_privacy.py -v

# Specific test class
pytest tests/test_privacy.py::TestPrivacyCompliance -v

# Stop on first failure
pytest tests/ -x

# Show print statements
pytest tests/ -s
```

### CI/CD Pipeline

All tests run automatically on:
- Push to main branch
- Pull request creation
- Scheduled daily run

**See `.github/workflows/` for configuration**

---

## Test Data Management

### Fixtures

```python
# tests/conftest.py
@pytest.fixture
def test_user():
    """Create test user with auth token."""
    user = User(
        username='testuser',
        email='test@example.com',
        password_hash=hash_password('TestPassword123!')
    )
    db.add(user)
    db.commit()
    
    token = create_access_token({'sub': user.id})
    user.auth_headers = {'Authorization': f'Bearer {token}'}
    
    yield user
    
    # Cleanup
    db.delete(user)
    db.commit()

@pytest.fixture
def test_metrics():
    """Generate realistic test metrics."""
    return {
        'cognitive_load': np.random.uniform(0, 1),
        'stress': np.random.uniform(0, 1),
        'fatigue': np.random.uniform(0, 1),
        'engagement': np.random.uniform(0, 1)
    }
```

---

## Quality Gates

**PR Merge Requirements:**
- ✅ All tests pass
- ✅ Coverage ≥ 80% (or improved from baseline)
- ✅ No new security issues
- ✅ Code review approval
- ✅ CI/CD pipeline green

---

## Reporting & Metrics

### Coverage Reports
```bash
# Generate HTML report
pytest tests/ --cov=backend --cov-report=html
# Open htmlcov/index.html in browser
```

### Performance Benchmarks
```bash
# Run performance tests
pytest tests/test_performance.py -v --benchmark-only
```

### Continuous Monitoring
- Coverage trends tracked on dashboard
- Performance regressions alerted
- Test flakiness monitored

---

**Last Updated**: 2026-08-20
