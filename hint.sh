python scripts/improve_hints.py audit                        # resumable; re-run to continue after any interruption
python scripts/improve_hints.py fix --from-report --dry-run  # preview
python scripts/improve_hints.py fix --from-report --apply    # resumable; writes meta.json per slug
python scripts/seed.py
