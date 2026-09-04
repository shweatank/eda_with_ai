import requests


BACKEND_URL = (
    "http://127.0.0.1:5000/validate"
)


def main():

    try:

        # Read SystemVerilog design
        with open(
            "decoder_2to4.sv",
            "r"
        ) as file:

            design_code = file.read()

        # Read cocotb testbench
        with open(
            "testbench_decoder_2to4.py",
            "r"
        ) as file:

            testbench_code = file.read()

        print(
            "Sending files to backend..."
        )

        response = requests.post(
            BACKEND_URL,
            json={
                "design": design_code,
                "testbench": testbench_code
            },
            timeout=180
        )

        print(
            f"\nHTTP Status: "
            f"{response.status_code}"
        )

        result = response.json()

        print(
            "\n========== DESIGN REVIEW =========="
        )

        print(
            "Status:",
            result.get(
                "design_review",
                {}
            ).get("status")
        )

        print(
            "Details:",
            result.get(
                "design_review",
                {}
            ).get("details")
        )

        print(
            "Issues:",
            result.get(
                "design_review",
                {}
            ).get("issues")
        )


        print(
            "\n========== TESTBENCH REVIEW =========="
        )

        print(
            "Status:",
            result.get(
                "testbench_review",
                {}
            ).get("status")
        )

        print(
            "Details:",
            result.get(
                "testbench_review",
                {}
            ).get("details")
        )

        print(
            "Issues:",
            result.get(
                "testbench_review",
                {}
            ).get("issues")
        )


        print(
            "\n========== SIMULATION =========="
        )

        print(
            "Status:",
            result.get(
                "simulation_validation",
                {}
            ).get("status")
        )

        print(
            "Details:",
            result.get(
                "simulation_validation",
                {}
            ).get("details")
        )


    except requests.exceptions.ConnectionError:

        print(
            "ERROR: Cannot connect to Flask backend."
        )

        print(
            "Make sure app.py is running."
        )


    except Exception as e:

        print(
            f"ERROR: {str(e)}"
        )


if __name__ == "__main__":

    main()