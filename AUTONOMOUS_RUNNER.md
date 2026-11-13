# Autonomous Voynich runner: guarded pilot

The workflow `.github/workflows/autonomous-voynich.yml` is **staged on this research branch** and does not run on the default branch until explicitly reviewed and merged. A daily schedule is specified, but **without the OPENAI_API_KEY repository secret it performs only the free integrity check**. ChatGPT Plus is not an API subscription; API calls incur separately billed usage.

When configured, the workflow runs the OpenAI Codex Action in a read-only GitHub job with workspace-only editing and a 55-minute limit. It uploads a patch artifact for review. It does NOT push, merge, create pull requests or grant GitHub write privileges to the agent. No automatic spend authorization is implied by this commit.

SECURITY LIMIT: `tools/research_guard.py` verifies corpus hashes and exposes the holdout exclusion set but does NOT prevent an unconstrained AI from reading held-out rows in the same checked-out files. **Therefore the agent job must NOT be enabled until a training-only dataset is physically materialized, with held-out content absent from the agent workspace**, and the action's job checks out only that dataset. This pilot intentionally fails closed: do not add OPENAI_API_KEY or merge until that isolation is implemented and tested. The holdout must remain confidential; no output may include its folio text.

Next: implement training-only corpus materialization in a separate, no-key job; pass only the filtered training artifact into the Codex job; add tests proving all reserved folios are absent; then review secret/billing and manually approve enabling schedule.
