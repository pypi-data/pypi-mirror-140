# NavAbilitySDK.py
Access NavAbility Cloud factor graph features from Python.

Note that this SDK and the related API are still in development. Please let us know if you have any issues.

# Installation

Install the NavAbilitySDK using pip:

```bash
pip install navabilitysdk
```

# Notes and FAQ

- **Why is the SDK camel-cased?** True, Python code should be snake-cased. This was a design decision to align all the SDKS. All the functions and fields should look the same, so you can easily switch from one language to another without having to read documentation. This may change in the future as we grow the SDKs.
- **Which user should I use?** The Guest user is open and free for everyone to use. We recommend testing with this user, because it doesn't require any authentication. Note though, that the data is cleared on a regular basis, and that everyone can see your test data (all Guest users are created equal), so don't put anything in there that that is sensitive.
- **I have sensitive data, how do I create a user?** Great question, the NavAbility services completely isolate data per user and you can create a user at any point. At the moment we create users on demand because the services are changing as we develop them, and we want to make sure we can let everyone know as they do. Send us an email at [info@navability.io](mailto:info@navability.io) and we'll create a user for you right away.
- **Why Asyncio?** We're working on integrating these into [Example Jupyter Notebooks](https://github.com/NavAbility/BinderNotebooks) which only support asynchronous GQL calls in the `gql` library. This design decision will be standardized in all our SDKs in the next release. Overally it's been a good call, and we'll expand on more asynchronous functionality as these SDKs develop.  
- Otherwise for any questions, comments, or feedback please feel free to email us at [info@navability.io](mailto:info@navability.io) or write an issue on the repo.  
# Example

This script will create variables and factors, list the graph, and solve the session for SLAM estimates.

> NOTES:
> * You'll need to start Python using `python -m asyncio` to support the `await` command.
> * You'll need numpy to run the example.

```python
from uuid import uuid4
import numpy as np
import json
from navability.entities import (
    Client,
    Factor,
    FactorData,
    FullNormal,
    NavAbilityHttpsClient,
    Pose2Pose2,
    PriorPose2,
    Variable,
    VariableType,
)
from navability.services import (
    addFactor,
    addVariable,
    solveSession,
    ls,
    lsf,
    waitForCompletion,
    getVariable
)

navability_client = NavAbilityHttpsClient()
client = Client("Guest", "MyUser", "Session_" + str(uuid4())[0:8])

# Create variables x0, x1, and x2
variables = [
    Variable("x0", VariableType.Pose2.value),
    Variable("x1", VariableType.Pose2.value),
    Variable("x2", VariableType.Pose2.value),
]

# Create factors between them
factors = [
        Factor(
            "x0f1",
            "PriorPose2",
            ["x0"],
            FactorData(
                fnc=PriorPose2(
                    Z=FullNormal(mu=np.zeros(3), cov=np.diag([0.1, 0.1, 0.1]))
                ).dump()  # This is a generator for a PriorPose2
            ),
        ),
        Factor(
            "x0x1f1",
            "Pose2Pose2",
            ["x0", "x1"],
            FactorData(
                fnc=Pose2Pose2(
                    Z=FullNormal(
                        mu=[1, 1, np.pi / 3], cov=np.diag([0.1, 0.1, 0.1])
                    )
                ).dump()  # This is a generator for a PriorPose2
            ),
        ),
        Factor(
            "x1x2f1",
            "Pose2Pose2",
            ["x1", "x2"],
            FactorData(
                fnc=Pose2Pose2(
                    Z=FullNormal(
                        mu=[1, 1, np.pi / 3], cov=np.diag([0.1, 0.1, 0.1])
                    )
                ).dump()  # This is a generator for a PriorPose2
            ),
        ),
    ]

# Get the result IDs so we can check on their completion
print("Adding variables and factors..\r\n")
variable_results = [await addVariable(navability_client, client, v) for v in variables]
factor_results = [await addFactor(navability_client, client, f) for f in factors]
result_ids = variable_results + factor_results

# Wait for them to be inserted if they havent already
print("Waiting for them to be loaded..\r\n")
await waitForCompletion(navability_client, result_ids, maxSeconds=120)

# Interrogate the graph
# Get the variables
print("Listing all the variables and factors in the session:\r\n")
vs = await ls(navability_client, client)
print("Variables: " + json.dumps(vs, indent=4, sort_keys=True))
# Get the factors
fs = await lsf(navability_client, client)
print("Factors: " + json.dumps(fs, indent=4, sort_keys=True))
# There's some pretty neat functionality with searching, but we'll save that for more comprehensive tutorials

# Request a SLAM multimodal solve and wait for the response
# Note: Guest sessions solve a little slower than usual because they're using some small hardware we put down for community use. Feel free to reach out if you want faster solving.
print("Requesting that the graph be solved to determine the positions of the variables (poses)...")
request_id = await solveSession(navability_client, client)
await waitForCompletion(navability_client, [request_id], maxSeconds=120)

# Get the solves positions of the variables (these are stores in the PPEs structure)
print("Getting the estimates of the variables (poses)...")
estimates = {v.label: (await getVariable(navability_client, client, v.label)).ppes['default'].suggested for v in variables}
print("Solved estimates for the positions:\r\n")
print(json.dumps(estimates, indent=4, sort_keys=True))
```
