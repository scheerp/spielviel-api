# Legacy Alembic Revisions

These revision files were archived after introducing the baseline migration
`2c13db88e4a1_add_target_type_to_player_search.py`.

Reason:

- The old migration chain contained broken historical steps and caused repeated
  migration failures on some environments.
- New development starts from the baseline revision `2c13db88e4a1`.

Important:

- Do not move these files back into `alembic/versions`.
- Existing databases should be stamped or migrated to `2c13db88e4a1`.
