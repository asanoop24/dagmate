def step_fn():
    print("Heello, I am a!!")
    raise ValueError("Kuch to locha hai!!")
    return 5, 10


if __name__ == "__main__":
    step_fn()
