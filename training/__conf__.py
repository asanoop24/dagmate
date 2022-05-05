steps = ["a", "b", "c", "d"]

inputs = {
    "a": {},
    "b": {},
    "c": {"x1": ("a", "x1"), "x2": ("a", "x2"), "start": ("b")},
    "d": {"x5": ("c", "x4")},
}

outputs = {"a": ["x1", "x2"], "c": ["x4", "x5"], "d": ["x6"]}

cron_schedule = "*/1 * * * *"
