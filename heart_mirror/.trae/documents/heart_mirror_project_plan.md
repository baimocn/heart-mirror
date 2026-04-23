# Heart Mirror Project Plan

## Project Overview
Heart Mirror is a Flask-based web application designed to help users explore their moral compass through interactive quizzes, personalized reports, and community engagement features. The application assesses users on six moral dimensions:正义感 (justice), 利他主义 (altruism), 规则遵从 (rule-following), 共情力 (empathy), 功利倾向 (utilitarianism), and 惩罚欲 (punishment).

## Current Project Structure

### Core Files
- **app.py**: Main application code with all routes and business logic
- **models.py**: Database models and data access functions
- **requirements.txt**: Project dependencies

### Frontend Assets
- **static/**
  - `script.js`: Client-side JavaScript
  - `style.css`: Styling
  - `questions.json`: Quiz questions and options
  - `图.jpg`: Image asset

### Templates
- **templates/**
  - `index.html`: Main landing page
  - `admin.html`: Admin dashboard
  - `admin_batches.html`: Donation batch management
  - `admin_flows.html`: Donation flow management
  - `admin_login.html`: Admin login page
  - `admin_questions.html`: Question management
  - `dilemmas.html`: Moral dilemma wall
  - `flows.html`: Donation flows display
  - `knowledge.html`: Knowledge base
  - `messages.html`: Messages page
  - `tasks.html`: Daily tasks page

### Database
- **database/heart_mirror.db**: SQLite database (implied by code)

## Key Features

### 1. Moral Assessment
- Interactive quiz with moral dilemma scenarios
- Six-dimensional moral scoring system
- Personalized detailed reports
- AI-generated reflections (simulated)

### 2. Donation System
- User donations with customizable amounts
- Batch management for donation campaigns
- Flow tracking for donation utilization
- Admin controls for managing donations

### 3. Community Features
- Moral dilemma wall for user-submitted scenarios
- Voting on dilemma options
- Community comments
- Knowledge base articles

### 4. Personal Growth
- Time capsules for saving moral profiles
- Daily micro-actions/tasks
- Points system for task completion
- Personalized recommendations

### 5. Admin Tools
- Question management (add, edit, delete)
- Donation batch and flow management
- User statistics and analytics
- Knowledge base management

## Technical Stack
- **Backend**: Python, Flask, SQLite
- **Authentication**: JWT (JSON Web Tokens)
- **Frontend**: HTML, CSS, JavaScript
- **Security**: bcrypt for password hashing
- **API**: RESTful endpoints

## Potential Areas for Improvement

### 1. Code Organization
- **Issue**: `app.py` is quite large (over 1000 lines) with mixed concerns
- **Solution**: Refactor into modular components:
  - `routes/` directory for different route groups
  - `services/` directory for business logic
  - `utils/` directory for helper functions

### 2. Database Management
- **Issue**: SQLite is suitable for development but may have limitations for production
- **Solution**: Consider migration to PostgreSQL or MySQL for better scalability

### 3. Frontend Enhancement
- **Issue**: Basic HTML/CSS/JavaScript implementation
- **Solution**: Implement a modern frontend framework like React or Vue.js for better user experience

### 4. Security Hardening
- **Issue**: Some security best practices could be improved
- **Solution**:
  - Implement CSRF protection
  - Add rate limiting for API endpoints
  - Improve input validation
  - Use HTTPS in production

### 5. Testing
- **Issue**: No automated tests found
- **Solution**: Implement unit tests and integration tests using pytest

### 6. Documentation
- **Issue**: Limited documentation
- **Solution**: Create comprehensive documentation including:
  - API documentation
  - Setup guide
  - Admin user guide
  - Developer documentation

### 7. Performance Optimization
- **Issue**: Potential performance bottlenecks with SQLite and large datasets
- **Solution**:
  - Implement caching for frequently accessed data
  - Optimize database queries
  - Consider asynchronous processing for heavy operations

## Implementation Roadmap

### Phase 1: Code Refactoring
1. Create directory structure for modular components
2. Split `app.py` into smaller, focused modules
3. Refactor database operations into separate service layer

### Phase 2: Database Optimization
1. Evaluate database performance
2. Consider migration to more scalable database
3. Optimize database schema and queries

### Phase 3: Frontend Modernization
1. Evaluate current frontend implementation
2. Select appropriate frontend framework
3. Implement responsive design and improved user experience

### Phase 4: Security Enhancement
1. Conduct security audit
2. Implement recommended security measures
3. Test for vulnerabilities

### Phase 5: Testing and Documentation
1. Develop comprehensive test suite
2. Create detailed documentation
3. Implement CI/CD pipeline

### Phase 6: Performance Tuning
1. Identify performance bottlenecks
2. Implement optimization strategies
3. Test and measure improvements

## Risk Assessment

### Technical Risks
- **Database scalability**: SQLite may not handle large user bases
- **Code maintainability**: Large monolithic codebase
- **Security vulnerabilities**: Potential for common web application security issues

### Operational Risks
- **Deployment complexity**: Lack of deployment documentation
- **Monitoring**: No apparent monitoring system
- **Backup strategy**: No clear data backup plan

### Mitigation Strategies
- **Phased approach**: Break down improvements into manageable phases
- **Testing**: Implement comprehensive testing before deployment
- **Documentation**: Create detailed documentation for all changes
- **Monitoring**: Implement logging and monitoring solutions

## Conclusion
Heart Mirror is a well-conceived application with a clear purpose and comprehensive feature set. By implementing the recommended improvements, the application can be transformed into a more scalable, maintainable, and secure platform that provides a better user experience while maintaining its core functionality.

The phased approach outlined in this plan allows for incremental improvements, minimizing disruption while maximizing the application's potential.