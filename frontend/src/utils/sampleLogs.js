export const SAMPLE_LOGS = {
  build: `[Pipeline] Start of Pipeline
[Pipeline] node
Running on agent-01 in /var/jenkins/workspace/my-app
[Pipeline] stage: Checkout
Cloning repository https://github.com/org/my-app.git
[Pipeline] stage: Build
[INFO] Scanning for projects...
[INFO] Building my-app 2.3.1
[INFO] Downloading: https://repo.maven.org/maven2/org/springframework/spring-core/5.3.21/spring-core-5.3.21.jar
[INFO] Downloaded: spring-core-5.3.21.jar (1.2 MB at 3.4 MB/s)
[INFO] --- maven-compiler-plugin:3.8.1:compile ---
[ERROR] COMPILATION ERROR :
[ERROR] src/main/java/com/example/UserService.java:[45,23] cannot find symbol
  symbol:   method getUserById(long)
  location: variable userRepository of type UserRepository
[ERROR] src/main/java/com/example/OrderController.java:[112,8] incompatible types: String cannot be converted to UUID
[ERROR] 2 errors
[INFO] BUILD FAILURE
[INFO] Total time: 23.4 s
[ERROR] Failed to execute goal org.apache.maven.plugins:maven-compiler-plugin:3.8.1:compile
[ERROR] -> [Help 1]
Finished: FAILURE`,

  test: `=== Test Run Started ===
Collecting tests...
pytest 7.4.0, Python 3.11.2

tests/test_auth.py::test_login_valid PASSED
tests/test_auth.py::test_login_invalid PASSED
tests/test_api.py::test_get_users PASSED
tests/test_api.py::test_create_user FAILED
tests/test_api.py::test_delete_user FAILED
tests/test_order.py::test_order_creation FAILED

FAILURES:
=== FAILED tests/test_api.py::test_create_user ===
AssertionError: assert 500 == 201
  Where 500 = response.status_code
  Expected 201 but got 500 (Internal Server Error)
  Response body: {"error": "duplicate key value violates unique constraint"}

=== FAILED tests/test_api.py::test_delete_user ===
AssertionError: assert 404 == 200
  Where 404 = response.status_code

=== FAILED tests/test_order.py::test_order_creation ===
TypeError: argument of type 'NoneType' is not iterable
  File "tests/test_order.py", line 78, in test_order_creation
    assert "order_id" in response.json()

=== short test summary info ===
FAILED tests/test_api.py::test_create_user
FAILED tests/test_api.py::test_delete_user
FAILED tests/test_order.py::test_order_creation
3 failed, 3 passed in 12.45s`,

  infrastructure: `[2024-01-15 09:23:11] Starting deployment pipeline
[2024-01-15 09:23:12] Pulling Docker image: registry.corp.com/my-app:latest
[2024-01-15 09:23:15] Error response from daemon: Get "https://registry.corp.com/v2/": 
  dial tcp 10.0.1.45:443: connect: connection refused
[2024-01-15 09:23:15] Retrying... (1/3)
[2024-01-15 09:23:20] Error response from daemon: Get "https://registry.corp.com/v2/": 
  dial tcp 10.0.1.45:443: connect: connection refused
[2024-01-15 09:23:20] Retrying... (2/3)
[2024-01-15 09:23:25] Error response from daemon: Get "https://registry.corp.com/v2/": 
  dial tcp 10.0.1.45:443: connect: connection refused
[2024-01-15 09:23:25] FATAL: Unable to pull Docker image after 3 retries
[2024-01-15 09:23:25] Attempting kubectl rollout...
[2024-01-15 09:23:26] Error from server (Forbidden): pods is forbidden: 
  User "ci-service-account" cannot list resource "pods" in API group "" in namespace "production"
[2024-01-15 09:23:26] RBAC permission denied
[2024-01-15 09:23:26] Pipeline failed with exit code 1
Finished: FAILURE`,
};
