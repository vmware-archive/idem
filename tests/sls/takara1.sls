foo:
  test.succeed_with_comment:
    - comment: {{ hub.takara.init.get(unit='main', path='foo/bar/baz') }}
