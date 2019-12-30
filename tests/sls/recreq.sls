first thing:
  test.nop

second thing:
  test.nop:
    - require:
      - test: first thing

third thing:
  test.nop:
    - require:
      - test: second thing

