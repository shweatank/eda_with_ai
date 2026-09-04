import requests


BACKEND_URL = "http://127.0.0.1:5000/validate"


def main():

    # Read SystemVerilog file
    with open(
        "decoder_2to4.sv",
        "r"
    ) as file:

        design_code = file.read()


    # Read Cocotb testbench
    with open(
        "testbench_decoder_2to4.py",
        "r"
    ) as file:

        testbench_code = file.read()


    print("Sending files to Flask backend...")


    response = requests.post(
        BACKEND_URL,
        json={
            "design": design_code,
            "testbench": testbench_code
        },
        timeout=180
    )


    result = response.json()


    print("\n========== DESIGN REVIEW ==========")

    print(
        "Status:",
        result["design_review"]["status"]
    )

    print(
        "Details:",
        result["design_review"]["details"]
    )

    print(
        "Issues:",
        result["design_review"]["issues"]
    )


    print("\n========== TESTBENCH REVIEW ==========")

    print(
        "Status:",
        result["testbench_review"]["status"]
    )

    print(
        "Details:",
        result["testbench_review"]["details"]
    )

    print(
        "Issues:",
        result["testbench_review"]["issues"]
    )


    print("\n========== SIMULATION ==========")

    print(
        "Status:",
        result["simulation_validation"]["status"]
    )

    print(
        "Details:",
        result["simulation_validation"]["details"]
    )


if __name__ == "__main__":

    main()