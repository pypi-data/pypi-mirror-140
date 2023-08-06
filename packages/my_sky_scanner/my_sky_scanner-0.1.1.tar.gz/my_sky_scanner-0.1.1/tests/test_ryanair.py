import pytest
from sky import Trip, get_raynair_info

def test_sum():
    assert sum([1, 2, 3]) == 6, "Should be 6"

if __name__ == "__main__":


    trip : Trip = Trip(2, 0, 0, 0, "2022-6-10", None, "MXP", "SUF")
    json = get_raynair_info(trip)

    print("Everything passed")