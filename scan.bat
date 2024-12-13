@echo off

@rem info:
@rem license:
@rem classify:
@rem license-diagnostics:
@rem unknown-license:
@rem processes:
@rem json-pp

scancode ^
--info ^
--license ^
--classify ^
--license-diagnostics ^
--unknown-licenses ^
--processes 4 ^
--json-pp scan_result.json ^
%~1