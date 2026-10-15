# YouTube Channel Monitor — BotCity Maestro Demo

A web automation bot that monitors YouTube channels and reports their stats directly to the BotCity Maestro orchestrator. Built to demonstrate Maestro's core features: Datapool, structured logs, alerts, and artifacts — all in a single, cohesive bot.

---

## What it does

For each YouTube channel in the queue, the bot:

- Navigates to the channel's main page using Firefox
- Collects subscriber count and total video count
- Logs the data to a structured Maestro execution log
- Sends an alert if the subscriber count cannot be read
- Uploads a screenshot of the channel page as an artifact
- Marks each Datapool item as done or failed
- Finishes the task with the appropriate status (`SUCCESS`, `PARTIALLY_COMPLETED`, or `FAILED`)

---

## Project structure

```
demo-yt/
├── bot.py               # Main bot — entry point
├── config.py            # Loads credentials from .env
├── setup_datapool.py    # Script to create and populate the Datapool
├── requirements.txt     # Python dependencies
└── .env                 # Your credentials (not committed)
```

---

## Requirements

- Python 3.8+
- Firefox installed
- A BotCity Maestro account ([sign up free](https://developers.botcity.dev/signup))

---

## Setup

### 1. Clone and install dependencies

```bash
git clone <your-repo-url>
cd demo-yt
pip install -r requirements.txt
```

### 2. Create your `.env` file

Create a `.env` file in the project root with your Maestro credentials:

```env
LOGIN=your_maestro_login
KEY=your_maestro_key
TASK_ID=your_task_id
```

- `LOGIN` and `KEY` are found in the Maestro portal under **Settings → Credentials**.
- `TASK_ID` is only required for local development runs. Get it from the Task Queue in the Maestro portal.

### 3. Create and populate the Datapool

Run `setup_datapool.py` once to create the `YoutubeChannels` Datapool and seed it with channels:

```bash
python setup_datapool.py
```

You can also add channels directly from the Datapool section in the Maestro portal.

---

## Running the bot

### Via Maestro (production)

Trigger the bot from the Maestro Task Queue. It will automatically pick the next pending channel from the `YoutubeChannels` Datapool queue. Run multiple instances to process the queue in parallel.

### Locally (development)

```bash
python bot.py
```

Credentials are loaded from `.env` via `config.py`. The bot connects to Maestro using `BotMaestroSDK.from_sys_args()` with the `.env` values as defaults.

---

## Maestro features demonstrated

| Feature | Where to see it |
|---|---|
| **Datapool** | `YoutubeChannels` queue — channels consumed one by one with individual status |
| **Execution Logs** | `YoutubeChannelLog` table — one row per channel processed |
| **Alerts** | Fired when a channel is not found or subscriber count is unavailable |
| **Artifacts** | Channel screenshot saved per execution |
| **Error handling** | Pass an invalid handle to see the full error + screenshot flow |
| **ROI Metrics** | `total_items`, `processed_items`, `failed_items` reported on every `finish_task` |

---

## Datapool schema — `YoutubeChannels`

| Field | Type | Displayed |
|---|---|---|
| `channel_handle` | TEXT | Yes |

## Execution log schema — `YoutubeChannelLog`

| Column | Description |
|---|---|
| `handle` | YouTube handle (e.g. `@botcity_br`) |
| `subscribers` | Subscriber count as displayed on the channel page |
| `videos` | Total video count as displayed on the channel page |

---

## Troubleshooting

**Firefox doesn't open**
Make sure Firefox is installed. `GeckoDriverManager` downloads the correct `geckodriver` automatically on first run.

**`ModuleNotFoundError: No module named 'distutils'`**
Run `pip install setuptools`. This is required on Python 3.12+.

**`ModuleNotFoundError: No module named 'botcity'`**
Run `pip install -r requirements.txt` inside your virtual environment.

**Datapool queue appears empty**
All items may already be in `DONE` or `ERROR` state. Run `setup_datapool.py` again to add new entries, or reset item states from the Maestro portal.

**Maestro authentication failed**
Double-check the `LOGIN` and `KEY` values in your `.env` file match what's shown in the Maestro portal under Settings.
