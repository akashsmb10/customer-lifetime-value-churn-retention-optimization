# Public dashboard

Live URL: https://akash-customer-retention-studio.akashsmb10.chatgpt.site

The public dashboard is a static browser implementation of the original Streamlit decision dashboard. It offers the same nine sections, verified analytical figures, scored customer profiles, and interactive retention scenario comparisons. It runs entirely in the browser and never trains a model on page load. The original Streamlit implementation remains available at app/app.py.

## Data integrity

`scripts/build_web.py` exports the executed results and saved tables into `web/data.js`, and copies verified analytical figures. The hosted dashboard uses the same 363 scored holdout customers. Its risk-only, value-only and combined targeting scenario calculations match the saved Python simulation at the tested default settings. Its random baseline uses exact expected exposure rather than the pipeline's average of 200 random samples; those approaches can differ slightly because of sampling error.

All costs, margin and intervention effectiveness remain explicit scenario assumptions. Forecast revenue is gross value, not profit. No treatment uplift, saved revenue or production banking results are claimed.

## Updating the browser dashboard

After changing or rerunning the analytics:

```powershell
.\.venv\Scripts\python.exe scripts\build_web.py
node --check web/app.js
node scripts/verify_web.mjs
```

Node.js is only needed for source verification and hosting preparation; visitors need only a browser. `scripts/prepare_node.py` can download a checksum-verified, task-local official Node LTS binary if Node is unavailable. It leaves system settings unchanged.

Source files are in `web/`. The Sites checkout is `.sites-publish/`, deliberately excluded from GitHub along with its nested Git metadata. Sites stores the deployment identity in that checkout's `.openai/hosting.json`. Future publishing must reuse that same Site, preserve public access, and follow the Sites source/package/deployment workflow. Never commit source-upload credentials.

## Verification

`reports/web_validation.json` records nine source-render checks, deterministic scenario parity, invalid-input checks, customer lookup and local-asset checks. These are executed JavaScript checks with a minimal DOM harness, not full browser visual tests. The optional WebMCP interface is feature-detected; supported-browser validation was unavailable and is not claimed. Sites reported a successful public production deployment.
