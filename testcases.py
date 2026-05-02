# Format: (input, expected_output, weight)

test_cases = [
    ("10 5\n", "15\n5\n50\n2.000000\n", 1),  # normal case
    ("20 4\n", "24\n16\n80\n5.000000\n", 1),
    ("5 0\n", "Error\n", 2)  # boundary case
]