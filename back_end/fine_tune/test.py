#!/usr/bin/env python3.11.2
"""lora tuner.

Copyright 2023 Zheyun Liu.
License(GPL)
Author: Zheyun Liu.
"""
import mytuner
from mytuner import chat


def main():
    """This is the main functioin."""
    # mytuner.fine_tuning(mytuner.fine_tuning_args)
    # mytuner.export_model(mytuner.export_model_args)
    mytuner.stream_chat(mytuner.chat_args)
    # chat_model = chat.ChatModel(mytuner.chat_args)
    # ans = chat_model.chat("3和1哪个数字更大", num_return_sequences=1)
    # print(ans)
    print("Hello world")


if __name__ == '__main__':
    main()
