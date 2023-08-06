
from robertcommonbasic.basic.data.utils import format_value

def test_format_value():

    print(f"format_value('1.234', '1') = {format_value('1.234', '1')}")
    print(f"format_value('1.234', '-2.0') = {format_value('1.234', '-2.0')}")
    print(f"format_value('-1.234', '2.0') = {format_value('-1.234', '2.0')}")
    print(f"format_value('-1.234', 'v*3') = {format_value('-1.234', 'v*3')}")
    print(f"format_value('测试', '1') = {format_value('测试', '1')}")
    print(f"format_value('测试', '1.2') = {format_value('测试', '1.2')}")
    print(f"format_value('1.234', '') = {format_value('1.234', '')}")

test_format_value()