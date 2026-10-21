# Examples

`input_format.json` is a **synthetic** input file showing the expected schema. It is
not taken from the original training data.

Input schema:

| Field | Required | Description |
|---|---|---|
| `id` or `name` | no | Optional identifier copied to the output |
| `mz` | yes | Comma-separated m/z values |
| `intensity` | yes | Comma-separated intensities, same length as `mz` |
| `label` | no | Optional binary label for evaluation |

Prediction output will add `score` and `probability` fields. The exact CLI and output
schema will be documented once the ported prediction pipeline lands.
