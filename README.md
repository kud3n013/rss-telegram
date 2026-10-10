# RSS to Telegram (GitHub Actions)

Sends new posts from any number of RSS/Atom feeds to your Telegram chat.
Free, no server, no feed limit. Feeds live in `feeds.yml`.

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
   Private repos only get 2,000 free minutes a month, which a run every 5 minutes would use up; if you go private, change the `cron:` line to every 30 minutes or less often.
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
After that it runs by itself every 5 minutes (the minimum GitHub allows; runs are often delayed a few minutes).

## Everyday use
- **Manage feeds from Telegram:** message your bot `/list`, `/add <url> [name]`, `/remove <number|name|url>`, `/test` (sends the newest post of a random feed, to check everything works; it links to the mirror page if that post is mirrored, otherwise it says it links to the original) or `/help`. The bot only obeys your own chat. Commands are read when the workflow runs, so replies usually take 5-10 minutes; to answer right away, press **Run workflow** in the Actions tab. `/add` checks that the link is a readable feed before saving it.
- **Add or remove a feed by hand:** edit `feeds.yml` on GitHub (pencil icon) and commit. Each feed is `- url: ...` with an optional `name:` (see the options at the top of the file). A new feed's existing posts are skipped; you only get new ones.
- **How much of each post you get:** each message has the title, source, and the start of the post (about 800 characters), plus a "Read more" link. Set the repo variable `EXCERPT_CHARS` (0-3000) to change it; `0` sends only the title and link. Set `LINK_PREVIEW` to `1` if you also want Telegram's link-preview card. Posts with a banner image (from the feed's media tags, an image attachment, or the first picture in the post) show it large above the text; set the repo variable `BANNERS` to `0` to turn that off.
- **Send the latest posts once:** Actions tab > **RSS to Telegram** > **Run workflow**, then type a number (1-20) in the **backfill** box. Every feed re-sends its newest N posts, even ones you've already received. `0` (the default) does nothing extra. Scheduled runs never backfill.
- **Get a few posts when adding a feed:** set the repo variable `NEW_FEED_BACKFILL` to N (1-20) under **Settings > Secrets and variables > Actions > Variables > New repository variable**. A newly added feed then sends its newest N posts instead of none. Unset or `0` keeps the default (nothing sent). Backfill runs may send more than the 25-message cap.
- **Change the schedule:** edit the `cron:` line in `.github/workflows/rss.yml`.
- **A feed isn't arriving:** open the latest run in the Actions tab and look for `FAILED` lines. Those name the feed and the reason.
- **Too many messages at once:** the script sends at most 25 per run (set `MAX_PER_RUN`); the rest follow on the next run.

## Notes
- State is kept in `seen.json` (and `feeds.yml` after chat commands), which the workflow commits automatically.
- GitHub pauses scheduled workflows in a public repo after 60 days without repo activity. The `seen.json` commits normally count as activity, but if the Actions tab ever shows the workflow as disabled, just re-enable it.
- Test locally without sending anything: `DRY_RUN=1 python notify.py` (add `BACKFILL=2` to preview a backfill)
- Run the offline tests: `python -m unittest tests.test_notify`

## Article mirror (reading pages on GitHub Pages)

Telegram caps a message at 4,096 characters, so long articles don't fit. With the mirror, every new post is
saved as Markdown, published as a page on your own GitHub Pages site, and the Telegram message carries the
title, source, as much of the text as fits in 4,096 characters, and a **Read more** link to that page.

### How a run works
`rss.yml` runs three jobs in order: **fetch** (feeds to `content/posts/<source>/<slug>.md`, committed) then
**build-deploy** (Hugo, noindex check, Pages) then **notify** (Telegram). Telegram is only contacted after the
deploy succeeded, and the notify step re-checks that the page answers 200, so the link never 404s. Build and
deploy only run when something changed; the notify job only runs when a post is waiting to be announced.
If anything fails midway, the next run picks up where it stopped and nothing is sent twice.

- **Content:** `mode: feed` converts the feed's own HTML, `mode: fetch` downloads the page and extracts the
  article (`trafilatura`, falling back to `readability-lxml`), `mode: auto` (default) uses the feed when it has
  at least `min_chars` of text. Images stay remote links; nothing binary is committed.
- **Blocked sites:** feeds marked `client: impersonate` use `curl_cffi` with a Chrome fingerprint. If a page still
  can't be fetched, the post is saved from the feed data and flagged `excerpt_only: true` (its page says so). Nothing
  more aggressive is attempted; failures are listed in the job summary.
- **Dedup:** the feed item's guid, per feed, in `seen.json`. File names are `<title-slug>-<6 hex of the guid hash>.md`.

### Marking posts read, and deletion
The bot can't see read receipts, so every message has a **✓ Read** button. The tap is picked up on the next run
(a few minutes later; the button then changes to "✓ Read · mirror removed within 24h").
- A post you marked read is removed **24 h** after the tap; one you never marked is removed **72 h** after it was
  announced. Set the repo variables `READ_TTL_HOURS` / `UNREAD_TTL_HOURS` to change this.
- A removed post is replaced by a tiny stub that redirects to the original article, so old Telegram links still
  work. Stubs are deleted after `STUB_DAYS` (default 30), after which the link 404s.
- Deleted articles stay in git history. In a public repo that history is readable on github.com; deleting a file
  is not the same as erasing it.

### Settings (repository variables)
`MIRROR_EXCERPT_CHARS` (0-4096, default 4096: fill the message), `READ_TTL_HOURS`, `UNREAD_TTL_HOURS`, `STUB_DAYS`,
`SITE_URL` (only if you use a custom domain), plus the existing `BANNERS`, `LINK_PREVIEW`, `NEW_FEED_BACKFILL`.
The manual **backfill** input mirrors and sends the newest N posts of every feed once (for testing).

### Setup for the mirror
**Settings > Pages > Build and deployment > Source: GitHub Actions.** Everything else is in the workflow.

### Add a feed
Message the bot `/add <url> [name]`, or add to `feeds.yml`:

    - url: https://example.com/feed
      name: Example
      mode: auto            # feed | fetch | auto
      client: plain         # plain | impersonate
      selector: "article"   # only if the generic extractor does poorly on this site
      remove: [".share", ".match-widget"]   # page elements to delete before extracting
      subtitle_selector: "p.standfirst"     # shown as the page's subtitle instead of in the body
      filter: {title_contains: [Epic]}   # optional

Check the result with `DRY_RUN=1 MIRROR=1 BACKFILL=1 python notify.py fetch` (files go to `content/posts/`).
After changing a feed's overrides, re-extract its posts that are still on the site: Actions > **RSS to
Telegram** > **Run workflow**, and type part of the feed's name or URL in **refetch** (e.g. `hltv`). The pages
are rebuilt in place (same links, same delete timer) and nothing is sent to Telegram again.

### Keeping the mirror out of search engines
Every generated page has `<meta name="robots" content="noindex, nofollow, noarchive, nosnippet">`, posts set
`<link rel="canonical">` to the original article, `robots.txt` disallows everything, and there is no sitemap and
no RSS/Atom output. `scripts/check_site.py` fails the build (and the tests) if any page lacks the tag or
`robots.txt` is missing or doesn't disallow everything.
Limits you should know: these are requests that well-behaved crawlers honor, **not access control**; anyone with
the link can read the pages. GitHub Pages can't send an `X-Robots-Tag` header, so the meta tag is what applies.
On a project site (`owner.github.io/repo/`) crawlers look for `robots.txt` at `owner.github.io/robots.txt`, so
the file only takes effect with a custom domain or a `<owner>.github.io` repository; the meta tag works either way.
The Markdown files in a public repo are visible on github.com whatever the site says.

### Tests
`python -m unittest tests.test_notify tests.test_mirror tests.test_site` (the site tests need `hugo` and are
skipped without it).
