# AI Metadata Inspector website asset note

The `screenshots/` folder in this repository is the single source of truth for AI Metadata Inspector visuals used in:

- this repository README
- the public page at `https://gaurox.dev/metadata-inspector/`

Do not maintain a separate edited screenshot set inside the website repo.

## Sync target

Source:

- `screenshots/` in this repository

Website copy:

- the `metadata-inspector/screenshots/` folder in your local Gaurox website workspace

## Sync method

Run the shared manual sync script from your local workspace:

- the screenshot sync script used by your Gaurox website checkout

The script clears the website screenshot copy for AI Metadata Inspector and recopies it from this repository.

## Rule for agents

- Update screenshots here first.
- If you modify the AI Metadata Inspector website page or its screenshot usage, always run the shared screenshot sync script before finishing the task.
- Then run the sync script.
- Do not edit the website screenshot copy by hand unless there is a one-off emergency fix.
