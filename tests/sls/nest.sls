req:
  test.nop:
    - require:
      - nest.again.another.test: baz

foo:
  nest.test.nop: []

bar:
  nest.again.test.nop: []

baz:
  nest.again.another.test.nop: []

quo:
  idem.init.create: []

