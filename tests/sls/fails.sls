fails:
  test.fail_without_changes

runs:
  test.nop:
    - onfail:
      - test: fails

bad:
  test.nop:
    - require:
      - test: fails