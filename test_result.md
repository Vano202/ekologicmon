#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: "I need to test the Air Quality Monitoring backend system comprehensively. The system includes backend components like Weather API integration, data processing pipeline, database operations, API endpoints, anomaly detection, CSV export, and background data collection."

backend:
  - task: "Weather API Integration"
    implemented: true
    working: true
    file: "/app/backend/services/weather_service.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "Successfully tested the Weather API integration. The system correctly connects to WeatherAPI.com using the provided API key. The health endpoint reports the Weather API as 'connected', and the manual data collection process successfully fetches data from the API. The logs confirm API requests are being made and processed correctly."

  - task: "Data Processing Pipeline"
    implemented: true
    working: true
    file: "/app/backend/services/data_processor.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "The data processing pipeline is working correctly. The system successfully fetches data from the Weather API, transforms it, detects anomalies, and stores the processed data in MongoDB. The logs show the complete processing flow with all steps executed in sequence. The test for complete data flow integration passed successfully."

  - task: "Database Operations"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "Database operations are working correctly. The system successfully connects to MongoDB and performs CRUD operations. The health check confirms the database is connected, and data is being stored and retrieved properly. Weather data, anomalies, logs, and daily statistics are all being stored correctly in their respective collections."

  - task: "API Endpoints"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "All API endpoints are working correctly. Successfully tested GET /api/current, GET /api/hourly, GET /api/daily, GET /api/anomalies, GET /api/logs, POST /api/collect, POST /api/export, and GET /api/health. All endpoints return the expected data structures and status codes. The endpoints handle parameters correctly and return appropriate error responses when needed."

  - task: "Anomaly Detection"
    implemented: true
    working: true
    file: "/app/backend/services/anomaly_detector.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "The anomaly detection system is working correctly. The system successfully detects anomalies based on statistical outliers and range violations. The anomaly detection process is integrated into the data processing pipeline, and anomalies are being stored in the database. The API endpoint for retrieving anomalies works correctly."

  - task: "CSV Export"
    implemented: true
    working: true
    file: "/app/backend/services/data_processor.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "The CSV export functionality is working correctly. Successfully tested exporting hourly data, daily statistics, and anomalies to CSV format. The exported CSV files have the correct headers and data formatting. The API endpoint for exporting data works correctly and returns the CSV data as a downloadable file."

  - task: "Background Data Collection"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "The background data collection process is working correctly. The system is configured to collect data every 5 minutes automatically. The health check shows the last collection timestamp, confirming that automatic data collection is occurring. Manual data collection also works correctly through the API endpoint."

metadata:
  created_by: "testing_agent"
  version: "1.0"
  test_sequence: 1
  run_ui: false

test_plan:
  current_focus:
    - "Weather API Integration"
    - "Data Processing Pipeline"
    - "Database Operations"
    - "API Endpoints"
    - "Anomaly Detection"
    - "CSV Export"
    - "Background Data Collection"
  stuck_tasks: []
  test_all: true
  test_priority: "high_first"

agent_communication:
  - agent: "testing"
    message: "I have completed comprehensive testing of the Air Quality Monitoring backend system. All components are working correctly. The system successfully integrates with WeatherAPI.com, processes and stores data in MongoDB, detects anomalies, and provides API endpoints for accessing the data. The CSV export functionality and background data collection are also working as expected. No issues were found during testing."
