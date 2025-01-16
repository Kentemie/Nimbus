def camel_case_to_snake_case(input_str: str) -> str:
    """
    Преобразует строку из CamelCase в snake_case.

    :param input_str: Строка в формате CamelCase.
    :return: Строка в формате snake_case.

    Примеры:
    >>> camel_case_to_snake_case("SomeSDK")
    'some_sdk'
    >>> camel_case_to_snake_case("RServoDrive")
    'r_servo_drive'
    >>> camel_case_to_snake_case("SDKDemo")
    'sdk_demo'
    """
    chars = []

    for curr_idx, char in enumerate(input_str):
        if curr_idx and char.isupper():
            nxt_idx = curr_idx + 1
            flag = nxt_idx >= len(input_str) or input_str[nxt_idx].isupper()
            prev_char = input_str[curr_idx - 1]

            if prev_char.isupper() and flag:
                pass
            else:
                chars.append("_")

        chars.append(char.lower())

    return "".join(chars)
