# BricksXploit

BricksXploit is an advanced security testing tool for Databricks environments. It allows security professionals to enumerate resources, scan for security issues, and generate comprehensive reports.

## Features

- **Comprehensive Scanning**: Enumerate users, groups, clusters, jobs, secret scopes, SQL warehouses, and more
- **Profile Management**: Store and switch between multiple workspace credentials and organizations
- **SQL Query Execution**: Run SQL statements and view results directly in the tool
- **Advanced Reporting**: Generate detailed security reports in multiple formats (JSON, CSV, Markdown)
- **Discord Integration**: Send notifications and reports to Discord via webhooks
- **Command-line Interface**: Run quick validations or scans from the command line
- **Interactive UI**: User-friendly menu system with rich formatting

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/bricksxploit.git
cd bricksxploit

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Interactive Mode

```bash
python -m bricksxploit
```

### Command-line Mode

```bash
# Validate credentials
python -m bricksxploit --workspace dbc-xxxx.cloud.databricks.com --apikey dapi123456789 --validate

# Generate a report
python -m bricksxploit --workspace dbc-xxxx.cloud.databricks.com --apikey dapi123456789 --output report.json

# Send notification to Discord
python -m bricksxploit --workspace dbc-xxxx.cloud.databricks.com --apikey dapi123456789 --notify discord

# Save credentials if valid
python -m bricksxploit --workspace dbc-xxxx.cloud.databricks.com --apikey dapi123456789 --validate --save --organization "Company Name"
```

## Features

### Profile Management

- Store multiple Databricks workspace credentials
- Organize profiles by organization
- Switch between profiles easily
- Validate credentials before saving

### Scanning Capabilities

- Full security scan of Databricks workspace
- Targeted scans for specific resource types
- SQL query execution and result viewing
- Scan for security issues and vulnerabilities

### Reporting

- Generate comprehensive security reports
- Export data in multiple formats (JSON, CSV, Markdown)
- Send reports to Discord for notification
- View scan history and results

## Configuration

BricksXploit stores configuration in `~/.bricksxploit/` directory:

- `config.json`: General configuration
- `profiles.json`: Stored profiles and credentials
- `history/`: Scan history and results

## Discord Integration

To enable Discord notifications:

1. Create a webhook in your Discord server
2. In BricksXploit, go to Configuration > Discord Settings
3. Enter your webhook URL
4. Test the integration with a validation notification

## Security Note

This tool is intended for legitimate security testing with proper authorization. Always ensure you have permission to test the Databricks environments you are scanning.

## License

This project is licensed under the MIT License - see the LICENSE file for details.