needed:
  test.nop

needs:
  test.nop:
    - require:
      - test: needed

fails:
  test.fail_without_changes

needs_fail:
  test.nop:
    - require:
      - test: fails