# AI Metadata Inspector website asset note

The `screenshots/` folder in this repository is the single source of truth for AI Metadata Inspector visuals used in:

- this repository README
- the public page at `https://gaurox.dev/metadata-inspector/`

Do not maintain a separate edited screenshot set inside the website repo.

## Sync target

Source:

- `E:\AI\AI_Metadata_Inspector_V\screenshots`

Website copy:

- `E:\AI\Gaurox_Website\metadata-inspector\screenshots`

## Sync method

Run the shared manual sync script:

- `E:\AI\sync-gaurox-website-screenshots.ps1`

The script clears the website screenshot copy for AI Metadata Inspector and recopies it from this repository.

## Rule for agents

- Update screenshots here first.
- If you modify the AI Metadata Inspector website page or its screenshot usage, always run `E:\AI\sync-gaurox-website-screenshots.ps1` before finishing the task.
- Then run the sync script.
- Do not edit `E:\AI\Gaurox_Website\metadata-inspector\screenshots` by hand unless there is a one-off emergency fix.
