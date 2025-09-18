#!/bin/bash

# Generate sample data for migration testing
set -e

echo "📁 Creating sample data for migration testing..."

# Create examples directory if it doesn't exist
mkdir -p examples/sample-files

# Create various file types to test migration
cat > examples/sample-files/user-data.json << 'EOF'
{
  "users": [
    {"id": 1, "name": "John Doe", "email": "john@example.com", "created": "2024-01-15"},
    {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "created": "2024-02-20"},
    {"id": 3, "name": "Bob Johnson", "email": "bob@example.com", "created": "2024-03-10"}
  ]
}
EOF

# Create a larger text file
cat > examples/sample-files/application-logs.txt << 'EOF'
2024-09-18 10:00:01 INFO  Application started successfully
2024-09-18 10:00:02 DEBUG Loading configuration from /etc/app/config.yaml
2024-09-18 10:00:03 INFO  Database connection established
2024-09-18 10:00:04 INFO  Starting web server on port 8080
2024-09-18 10:00:05 INFO  Ready to accept connections
2024-09-18 10:15:23 INFO  Processing user request: GET /api/users
2024-09-18 10:15:24 INFO  Request completed successfully in 142ms
2024-09-18 10:30:45 WARN  High memory usage detected: 85%
2024-09-18 10:30:46 INFO  Garbage collection completed
2024-09-18 10:45:12 ERROR Failed to connect to external service: timeout
2024-09-18 10:45:13 INFO  Retrying connection attempt 1/3
2024-09-18 10:45:15 INFO  Connection retry successful
EOF

# Create a CSV file
cat > examples/sample-files/sales-data.csv << 'EOF'
Date,Product,Quantity,Price,Customer
2024-09-01,Widget A,5,29.99,Customer1
2024-09-01,Widget B,3,45.50,Customer2
2024-09-02,Widget A,2,29.99,Customer3
2024-09-02,Widget C,1,89.99,Customer1
2024-09-03,Widget B,4,45.50,Customer4
EOF

# Create an image file (simple text-based "image" for testing)
cat > examples/sample-files/company-logo.txt << 'EOF'
   _____ _                 _   __  __ _                 _   _             
  / ____| |               | | |  \/  (_)               | | (_)            
 | |    | | ___  _   _  __| | | \  / |_  __ _ _ __ __ _| |_ _  ___  _ __  
 | |    | |/ _ \| | | |/ _` | | |\/| | |/ _` | '__/ _` | __| |/ _ \| '_ \ 
 | |____| | (_) | |_| | (_| | | |  | | | (_| | | | (_| | |_| | (_) | | | |
  \_____|_|\___/ \__,_|\__,_| |_|  |_|_|\__, |_|  \__,_|\__|_|\___/|_| |_|
                                        __/ |                            
                                       |___/                             
EOF

# Create configuration file
cat > examples/sample-files/app-config.yaml << 'EOF'
application:
  name: "migration-demo-app"
  version: "1.0.0"
  environment: "production"

database:
  host: "db.example.com"
  port: 5432
  name: "appdb"
  ssl: true

cache:
  redis:
    host: "cache.example.com"
    port: 6379
    ttl: 3600

logging:
  level: "INFO"
  format: "json"
  output: "stdout"
EOF

echo "✅ Sample files created in examples/sample-files/"
ls -la examples/sample-files/