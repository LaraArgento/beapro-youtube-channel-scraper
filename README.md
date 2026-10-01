# YouTube Channel Scraper: a BotCity CSV Showcase

This is a simple bot that reads a list of YouTube channels from a CSV file and writes the result of each one to a new CSV file. It's a demo, not a production scraper. The YouTube part is kept small on purpose, so the focus stays on how the bot reads items from a CSV, handles errors and records the status of each item.

## 🎬 What the bot does

For each row in the input CSV, the bot:

1. Reads the `channel` column, for example `botcity_br`
2. Opens `https://www.youtube.com/@<channel>` in the browser
3. Reads the channel name, subscriber count and video count from the page header
4. Writes the row to the result CSV with its status and message

These cases are built in so you can see how the bot handles each outcome:

| Outcome | When it happens | `STATUS` in the result CSV |
|---|---|---|
| ✅ Success | The channel exists and its data was read | `SUCCESS` |
| ⚠️ Business error | The channel doesn't exist (the page returns "404 Not Found") | `BUSINESS EXCEPTION` |
| 💥 System error | A **simulated random failure** on about 1 in 20 items | `SYSTEM EXCEPTION`; the bot restarts and moves on to the next row |

The random system error is intentional. It lets you see error handling, restarts and status tracking without having to break anything.

## 🗂️ Input and output

**Input:** the bot reads [resources/youtube-channels-15.csv](resources/youtube-channels-15.csv), a small set of 13 channels for a quick run. The file has one column, `channel`. It includes a channel name that doesn't exist, `aaaa_ThisChannelDoesNotExist`, so that at least one row raises a business error.

To use the larger set, [youtube-channels-170.csv](resources/youtube-channels-170.csv), or your own file, change the path in the `CSVSource(...)` line at the bottom of [framework/datasources.py](framework/datasources.py). Any CSV with a `channel` column works.

**Output:** the bot writes `output/CSV_BotCity_task-{task_id}_date-{timestamp}.csv`. It has the original columns plus `TIMESTAMP`, `STATUS` and `MESSAGE`. For a success, `MESSAGE` holds the channel name, subscriber count and video count. For an error, it holds the error message. When the bot runs connected to BotCity Orchestrator, the file is uploaded as a Result File at the end of the task.

---

## About the framework

This bot is built on **BeaPro** (BotCity Enterprise Automation Process), a production-ready automation framework built on top of BotCity. BeaPro provides state management and structured error handling, and it integrates with BotCity Orchestrator. The rest of this README documents the framework.

## 🚀 Features

- **State Management**: Built-in state tracking for success/error counts and execution status
- **Structured Exception Handling**: Automatic handling of business exceptions, system exceptions, and interruption requests
- **Default Logging**: File-based and BotCity Orchestrator logging with timestamps
- **CSV Data Source**: Reads items from a CSV file and writes a result CSV with the status of each item
- **Error Reporting**: Screenshot capture and error reporting to BotCity Orchestrator
- **Graceful Finalization**: Automatic cleanup, result file uploads, and task completion
- **Restart Capability**: System exception recovery with automatic restart
- **Flexible structure**: All the files are in the framework folder, so you can add your own files and folders as needed

## 📁 Project Structure

```
BeaPro/
├── bot.py                      # Main automation orchestrator
├── framework/                  # Core framework modules
│   ├── state.py               # State management and BotCity SDK setup
│   ├── exceptions.py          # Custom exception classes
│   ├── datasources.py         # Data source implementations (CSV)
│   ├── process.py             # Main automation logic (ADD YOUR CODE HERE)
│   ├── initialize.py          # Initialization and setup
│   ├── finalize.py            # Cleanup and finalization
│   ├── status_handling.py     # Exception and success handlers
│   └── logger.py              # Logging configuration
├── resources/                  # Sample YouTube channel lists (input CSV files)
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables for testing (credentials)
├── .gitignore                  # Git ignore file
├── output/                     # Generated output files and logs
├── temp/                       # Temporary files (screenshots, etc.)
└── build/                      # Build scripts
```

## 🛠️ Installation

### Prerequisites

- Python 3.7+
- BotCity account (for Orchestrator integration)

### Setup Steps

1. **Clone or download the project**

2. **Install dependencies**
   - Run: `pip install -r requirements.txt`

3. **Configure environment variables**
   - Edit the `.env` file with your BotCity credentials
   - Required variables: SERVER, LOGIN, KEY, TASK_ID

4. **Configure your data source**
   - At the bottom of `framework/datasources.py`, set the path of the input CSV in the `CSVSource(...)` line

## 📝 Usage

### Quick Start

1. **Add your automation steps** in `framework/process.py`
   - The `process_item(item)` function is where you implement your automation logic
   - Access item data using dictionary keys: `item['id']`, `item['name']`, etc.

2. **Run locally** (test mode)
   - Execute: `python bot.py`
   - No authentication required for testing

3. **Run with BotCity Orchestrator**
   - Build using: `build/build.bat`
   - Deploy to BotCity Orchestrator
   - Create and run a task

### Execution Modes

The framework supports three execution modes:

1. **Test Mode** (Local without authentication)
   - No `.env` configuration needed
   - Mock objects for Orchestrator features
   - Ideal for development and testing

2. **Local with Authentication**
   - Configure `.env` with credentials
   - Full Orchestrator integration
   - Useful for debugging

3. **BotCity Runner**
   - Deployed to BotCity Orchestrator
   - Production environment
   - Automatic credential injection

## 🎯 Framework Components

### Core Modules

#### `bot.py` - Main Orchestrator
The entry point that coordinates the entire automation flow:
- Initializes the environment
- Iterates through data source items
- Handles exceptions automatically
- Finalizes and reports results

#### `framework/process.py` - Automation Logic
**⭐ This is where you add your automation steps!**

The `process_item(item)` function is called for each item in your data source. This is the main file you'll customize with your specific automation logic.

#### `framework/state.py` - State Management
Manages execution state:
- Success/error counters
- Current item tracking
- Bot instances (WebBot, DesktopBot)
- Interruption checking
- Task status computation

#### `framework/exceptions.py` - Exception Types
Three custom exception types:
- **`BusinessException`**: Validation errors, invalid data (continues processing next item)
- **`SystemException`**: Technical failures (triggers restart and continues)
- **`InterruptException`**: Orchestrator interruption requests (stops gracefully)

#### `framework/datasources.py` - Data Sources
**CSVSource**: Reads from CSV files
- Returns items as dictionaries
- Generates result CSV with status tracking
- Automatic timestamp and status columns

#### `framework/initialize.py` - Initialization
Sets up the automation environment:
- Creates output/temp folders
- Configures logging
- Initializes WebBot/DesktopBot
- Handles restart scenarios
- Opens applications and logs into systems

#### `framework/finalize.py` - Finalization
Gracefully ends the automation:
- Closes browsers and applications
- Uploads result files to Orchestrator
- Sends final status report
- Computes task completion status (SUCCESS, FAILED, PARTIALLY_COMPLETED)

#### `framework/status_handling.py` - Exception Handlers
Handles different exception types:
- Logs errors with detailed information
- Sends alerts to Orchestrator
- Captures screenshots on errors
- Reports success/failure to data source
- Customizable handlers for different scenarios

#### `framework/logger.py` - Logging
Configures comprehensive logging:
- File-based logs with timestamps in output folder
- BotCity Orchestrator execution logs
- Formatted output with module/function names
- Automatic log file creation with task ID and timestamp

## 🔧 Customization

### Adding Custom Exception Handling

In `framework/status_handling.py`, you can customize the handlers:
- Add email notifications
- Update external databases
- Send custom alerts
- Implement retry logic
- Add business-specific error handling

### Creating Custom Data Sources

Inherit from `BaseSource` in `framework/datasources.py`:
- Implement `__iter__` and `__next__` methods
- Add `report_success` and `report_error` methods
- Connect to databases, APIs, or other data sources

### Configuring Browser Settings

In `framework/initialize.py`, modify `init_webbot()`:
- Set headless mode (True/False)
- Choose browser (CHROME, FIREFOX, EDGE)
- Configure driver paths
- Set browser options and preferences

## 📊 Data Source Format

### CSV Format

Your CSV file should have headers in the first row. The framework reads each row as a dictionary where column names become keys.

**Example CSV structure:**
- First row: Column headers (id, name, email, status, phone, city)
- Subsequent rows: Data values
- Access in code: `item['column_name']`

## 🎭 Exception Handling Flow

```
For each item:
  ├─ Try: process_item(item)
  │   ├─ Success → register_success()
  │   └─ Exception:
  │       ├─ InterruptException → handle_interrupt_requested() → STOP
  │       ├─ BusinessException → handle_business_exception() → CONTINUE
  │       └─ SystemException → handle_system_exception() → RESTART → CONTINUE
  └─ Next item
```

**Flow Details:**
- **Success**: Registers success, updates counters, continues to next item
- **InterruptException**: Logs warning, sends alert, stops execution gracefully
- **BusinessException**: Logs error, sends alert, captures screenshot, continues to next item
- **SystemException**: Logs error, sends alert, captures screenshot, restarts initialization, continues

## 📈 Output Files

The framework generates several output files in the `output/` folder:

- **Log files**: `Log_BotCity_task-{task_id}_date-{timestamp}.log`
  - Contains detailed execution logs with timestamps
  - Includes all info, warning, and error messages
  - Formatted with module and function names

- **CSV results**: `CSV_BotCity_task-{task_id}_date-{timestamp}.csv`
  - Original data plus STATUS, MESSAGE, and TIMESTAMP columns
  - Shows which items succeeded or failed
  - Includes error messages for failed items

- **Screenshots**: Stored in `temp/` folder
  - Captured automatically on exceptions
  - Named with error timestamp
  - Uploaded to BotCity Orchestrator

All files are automatically uploaded to BotCity Orchestrator as Result Files at the end of execution.

## 🔍 Monitoring and Debugging

### Local Testing
1. Run without `.env` configuration for test mode
2. Check console output for execution flow
3. Review log files in `output/` folder
4. Inspect CSV results for item status
5. Check `temp/` folder for error screenshots

### BotCity Orchestrator
1. View real-time logs in Execution Log
2. Receive alerts for exceptions (ERROR for failures, WARN for interruptions)
3. Download result files after completion
4. Monitor task status (SUCCESS, FAILED, PARTIALLY_COMPLETED)
5. View execution metrics (total items, processed, failed)

## 🚨 Common Issues

### "File path is invalid" when building
- Ensure the build script points to the correct `.zip` file
- Check that the build process completed successfully
- Verify the file path uses correct Windows path format

### Items not processing
- Verify data source configuration in `framework/datasources.py`
- Check CSV file path and format (must have headers)
- Check if data source file exists in resources folder

### Authentication errors
- Verify `.env` file has correct credentials
- Check SERVER, LOGIN, KEY, and TASK_ID values
- Ensure task exists in BotCity Orchestrator

## 🔗 Resources

- [BotCity Documentation](https://documentation.botcity.dev/)
- [BotCity Maestro SDK](https://documentation.botcity.dev/maestro/)
- [BotCity Plugins](https://documentation.botcity.dev/plugins/)
- [BotCity Community](https://community.botcity.dev/)

## 💡 Tips and Best Practices

- **Use descriptive exception messages**: They appear in alerts and logs, making debugging easier
- **Log frequently**: Add logger.info() statements at key points in your automation
- **Test locally first**: Use test mode before deploying to production
- **Customize handlers**: Add your own logic to exception handlers and success registration
- **Monitor state**: Use `STATE` object to track execution progress and access bot instances
- **Use appropriate exceptions**: BusinessException for data issues, SystemException for technical failures
- **Keep process_item focused**: Put your main automation logic in `process_item()`, use other modules for setup
- **Review output files**: Check logs and CSV results after each run to verify behavior
- **Update data sources**: Modify `datasources.py` to connect to your specific data sources if needed
- **Handle interruptions**: The framework checks for interruption requests automatically

## 📞 Support

For issues or questions:
- Check the BotCity documentation
- Review the framework code comments and docstrings
- Test in different execution modes to isolate issues
- Check log files for detailed error information

## License
This project is licensed under the Apache 2.0 License - see the LICENSE file for details.