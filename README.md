# RSS to Telegram (GitHub Actions)

Sends new posts from any number of RSS/Atom feeds to your Telegram chat.
Free, no server, no feed limit. Feeds live in `feeds.txt`.

## Setup (about 10 minutes)

### 1. Create your Telegram bot
1. In Telegram, open **@BotFather** and send `/newbot`. Follow the prompts.
2. Copy the **bot token** it gives you.
3. Open your new bot and press **Start** (send it any message). Bots can't message you until you do this.

### 2. Get your chat ID
Open this URL in a browser, with your token filled in:

    https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates

Look for `"chat":{"id": 123456789, ...}`. That number is your chat ID.
(If the result is empty, send your bot another message and reload.)

### 3. Put the files on GitHub
1. Create a new repository on GitHub. Public is easiest: Actions minutes are unlimited.
   Private also works within the free monthly allowance (a run every 30 minutes uses roughly 1,500 minutes per month, under the 2,000 limit).
2. Upload everything from this folder, keeping the structure, **including the hidden `.github/workflows/rss.yml`**.

### 4. Add your secrets
In the repo: **Settings > Secrets and variables > Actions > New repository secret**. Add two:
- `TELEGRAM_BOT_TOKEN`: the token from step 1
- `TELEGRAM_CHAT_ID`: the number from step 2

### 5. Allow the workflow to save its state
**Settings > Actions > General > Workflow permissions**: choose **Read and write permissions**, then Save.

### 6. Run it
Go to the **Actions** tab, open **RSS to Telegram**, press **Run workflow**.
You should get "RSS bot is live, tracking N feeds" in Telegram within a minute.
After that it runs by itself every 30 minutes.

## Everyday use
- **Add or remove a feed:** edit `feeds.txt` on GitHub (pencil icon) and commit. A new feed's existing posts are skipped; you only get new ones.
- **Change the schedule:** edit the `cron:` line in `.github/workflows/rss.yml`.
- **A feed isn't arriving:** open the latest run in the Actions tab and look for `FAILED` lines. Those name the feed and the reason.
- **Too many messages at once:** the script sends at most 25 per run (set `MAX_PER_RUN`); the rest follow on the next run.

## Notes
- State is kept in `seen.json`, which the workflow commits automatically.
- GitHub pauses scheduled workflows in a public repo after 60 days without repo activity. The `seen.json` commits normally count as activity, but if the Actions tab ever shows the workflow as disabled, just re-enable it.
- Test locally without sending anything: `DRY_RUN=1 python notify.py`
