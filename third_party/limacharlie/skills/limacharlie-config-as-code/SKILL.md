---
name: limacharlie-config-as-code
description: Manage a LimaCharlie organization's configuration as code with the limacharlie CLI's `sync` command. Pull D&R rules, false-positive rules, extensions and other resources into YAML, review and edit them, dry-run the push, and apply it only after approval. Use for "back up my org config", "put our rules in git", "copy rules to another org" and configuration drift reviews.
---

# Organization configuration as code

Read the `limacharlie` skill first for the connections, org selection, the approval rule and the rules for the limacharlie CLI on the shared computer. This workflow needs the CLI: check with `limacharlie --version`. If it is missing, ask before installing it (`pipx install limacharlie`), and ask the user to sign in themselves (`limacharlie auth login --oauth`).

- `sync pull` only reads.
- `sync push` changes the org and needs a reviewed dry-run plus approval.
- `sync push --force` also **deletes** everything in the org that is not in the file.

## Pull

Pull only the resource types the task needs, and always pass the org explicitly:

```bash
limacharlie --oid <OID> sync pull --config-file /workspace/limacharlie/<org>/org.yaml --hive-dr-general --hive-fp --extensions
```

`limacharlie sync pull --ai-help` lists every resource flag.

**Keep credentials out of files.** These flags write credentials into the YAML:

- `--hive-secret`: secret values
- `--installation-keys`: sensor enrollment keys
- `--outputs`: destination tokens and passwords
- `--org-values`: third-party API keys
- `--hive-cloud-sensor`, `--hive-external-adapter`, `--hive-extension-config`: adapter and extension configs, which can embed API keys
- `--yara`, `--hive-yara`: YARA sources, whose locators can embed access tokens
- `--all`: includes all of the above

Files on the Bot computer are visible to every Bot on the account, so treat pulling any of these as reading a credential. Use them only with approval, delete the file when the task is done, and never commit it to a repository or share it.

Before committing any pulled file, scan it for anything that looks like a credential, and point it out instead of committing it.

## Review and edit

Treat the YAML like code. Make focused edits, keep unrelated resources unchanged, and show the user a diff. New or changed D&R and FP rules go through the validation and testing steps in the `limacharlie-detection-engineering` skill before they are pushed.

## Push

1. **Dry-run** with exactly the flags you will use for the real push:

   ```bash
   limacharlie --oid <OID> sync push --config-file org.yaml --hive-dr-general --hive-fp --dry-run
   ```

2. **Approve.** The approval prompt names the org (name and OID) and gives counts of what will be added, changed and removed, per resource type. The help text holds the full dry-run summary.
3. **Apply** the same command without `--dry-run`. Add `--force` only when the user explicitly wants resources missing from the file deleted from the org, and list those resources in the approval.
4. **Verify** by pulling again with the same flags into a new file and diffing it against what was pushed. Report any difference.

## Copying configuration between orgs

Pull from the source org, review the file, then dry-run and push to the destination org, restating both org names and OIDs. Each destination org needs its own dry-run and its own approval. Never use `--force` on a destination unless the user wants it to mirror the source exactly, and only after showing what would be deleted.
