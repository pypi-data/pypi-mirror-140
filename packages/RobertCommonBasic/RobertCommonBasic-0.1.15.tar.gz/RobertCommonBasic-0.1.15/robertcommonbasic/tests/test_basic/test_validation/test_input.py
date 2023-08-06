from robertcommon.basic.validation.input import ensure_not_none_int, ensure_int, assert_int, assert_not_none_int, ensure_of, ensure_not_none_of

config = {'interval': '0.3'}
interval = ensure_not_none_of('interval', config, float)
print(interval)