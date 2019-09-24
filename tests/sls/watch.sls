changes:
  test.succeed_with_changes

watch_changes:
  test.nop:
    - watch:
      - test: changes
